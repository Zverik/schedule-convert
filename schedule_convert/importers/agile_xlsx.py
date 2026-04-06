from ..model import Conference, Room, Speaker, Event
from openpyxl import Workbook
from openpyxl.reader.excel import load_workbook
import re
from datetime import datetime
from slugify import slugify


RE_TIME = re.compile(r'^\s*(\d\d?)[:.](\d\d)\s*$')
RE_DATE = re.compile(r'^\s*(?:(\d{2,4})-)?(\d\d?)-(\d\d?)\s*$')


class AgileXlsImporter:
    name = 'agile'

    def __init__(self):
        pass

    def check(self, head):
        return head.startswith('PK') and '[Content_Types].xml' in head

    def parse(self, fileobj) -> Conference:
        wb = load_workbook(fileobj, read_only=True, data_only=True)
        ws = wb.active

        conf = Conference(None)
        speakers = {}
        rooms = {}
        day = None
        room = None
        track = None
        event = None
        first_row = True
        c: dict[int, str] = {}

        DAY = 'day'
        START_TIME = 'start time'
        END_TIME = 'end time'
        TITLE = 'title'
        SLUG = 'short title'
        DESCRIPTION = 'abstract (topic)'
        ROOM = 'room'
        TRACK = 'type'
        SPEAKER = 'organiser(s)'
        URL = 'website'

        for rrow in ws.values:
            if first_row:
                for i, name in enumerate(rrow):
                    if name and name.strip():
                        c[i] = name.strip().lower()
                first_row = False
                continue

            row = {c[i]: v for i, v in enumerate(rrow) if i in c}
            print(row)

            if day is None and not row.get(DAY):
                continue
            if row.get('day'):
                m = RE_DATE.match(row[DAY])
                if not m:
                    raise ValueError('Wrong date, expecting YYYY-MM-DD: "{}"'.format(row[DAY]))
                if m.group(1):
                    year = int(m.group(1))
                else:
                    year = datetime.now().year
                new_day = datetime(year, int(m.group(2)), int(m.group(3)))
                if new_day != day:
                    if event:
                        if not event.duration:
                            raise ValueError('Missing duration for event "{}"'.format(event.title))
                        conf.events.append(event)
                        event = None
                    day = new_day
                    room = None
                    track = None
            if room is None and not row.get(ROOM):
                continue
            if row.get(ROOM):
                new_room = row[ROOM].strip()
                if new_room not in rooms:
                    rooms[new_room] = Room(new_room)
                if room != rooms[new_room]:
                    if event:
                        if not event.duration:
                            raise ValueError('Missing duration for event "{}"'.format(event.title))
                        conf.events.append(event)
                        event = None
                    room = rooms[new_room]

            if row.get(TRACK):
                track = row[TRACK].strip()
                if track == '-':
                    track = None

            if not row.get(TITLE) or not row.get(TITLE):
                continue
            m = RE_TIME.match(row[START_TIME])
            if not m:
                raise ValueError('Wrong time "{}"'.format(row[START_TIME]))

            start = day.replace(hour=int(m.group(1)), minute=int(m.group(2)))
            if event:
                if not event.duration:
                    duration = (start - event.start).total_seconds() // 60
                    if duration < 3 or duration > 500:
                        raise ValueError('Duration of event "{}" is inadequate: {}'.format(
                            event.title, duration))
                    event.duration = int(duration)
                conf.events.append(event)

            event = Event(row[TITLE].strip(), id=len(conf.events)+1)
            event.room = room
            event.start = start
            event.track = track

            duration = None
            if row.get(END_TIME):
                m2 = RE_TIME.match(row[END_TIME])
                if m2:
                    end = day.replace(hour=int(m2.group(1)), minute=int(m2.group(2)))
                    duration = (end - start).total_seconds() // 60
            elif row.get('duration'):
                try:
                    duration = round(float(row['duration'].strip()))
                except ValueError:
                    pass
            if duration and 3 <= duration <= 300:
                event.duration = int(duration)

            if row.get(DESCRIPTION):
                event.description = row[DESCRIPTION].strip()
            if row.get(URL):
                event.url = row[URL].strip()
            if row.get(SLUG):
                event.slug = slugify(row[SLUG].strip())

            speakerstr = row.get(SPEAKER)
            if speakerstr:
                if ',' in speakerstr:
                    speakerstr = [s.strip() for s in speakerstr.split(',')]
                elif ';' in speakers:
                    speakerstr = [s.strip() for s in speakerstr.split(';')]
                else:
                    speakerstr = [speakerstr.strip()]
                for sp in speakerstr:
                    if sp not in speakers:
                        speakers[sp] = Speaker(sp, id=len(speakers)+1)
                    event.speakers.append(speakers[sp])

        if event:
            if not event.duration:
                raise ValueError('Missing duration for event "{}"'.format(event.title))
            conf.events.append(event)
        return conf
