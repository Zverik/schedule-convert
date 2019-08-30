from ..model import Conference, Room, Speaker, Event
from datetime import datetime
import csv
import re


RE_TIME = re.compile(r'^\s*(\d\d?)[:.](\d\d)\s*$')
RE_DATE = re.compile(r'^\s*(?:(\d{2,4})-)?(\d\d?)-(\d\d?)\s*$')


class CSVImporter:
    name = 'csv'

    def __init__(self):
        self.delimiter = ','

    def check(self, head):
        line = head.splitlines()[0]
        self.delimiter = ','
        titles = line.split(',')
        if 'room' not in titles:
            titles = line.split(';')
            self.delimiter = ';'
        for k in ('day', 'room', 'start', 'title'):
            if k not in titles:
                return False
        return True

    def parse(self, fileobj):
        conf = Conference(None)
        speakers = {}
        rooms = {}
        day = None
        room = None
        track = None
        event = None
        for row in csv.DictReader(fileobj, delimiter=self.delimiter):
            if day is None and not row.get('day'):
                continue
            if row.get('day'):
                m = RE_DATE.match(row['day'])
                if not m:
                    raise ValueError('Wrong date, expecting YYYY-MM-DD: "{}"'.format(row['day']))
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
            if room is None and not row.get('room'):
                continue
            if row.get('room'):
                new_room = row['room'].strip()
                if new_room not in rooms:
                    rooms[new_room] = Room(new_room)
                if room != rooms[new_room]:
                    if event:
                        if not event.duration:
                            raise ValueError('Missing duration for event "{}"'.format(event.title))
                        conf.events.append(event)
                        event = None
                    room = rooms[new_room]

            if row.get('track'):
                track = row['track'].strip()

            if not row.get('title') or not row.get('start'):
                continue
            m = RE_TIME.match(row['start'])
            if not m:
                raise ValueError('Wrong time "{}"'.format(row['start']))

            start = day.replace(hour=int(m.group(1)), minute=int(m.group(2)))
            if event:
                if not event.duration:
                    duration = (start - event.start).total_seconds() // 60
                    if duration < 3 or duration > 120:
                        raise ValueError('Duration of event "{}" is inadequate: {}'.format(
                            event.title, duration))
                    event.duration = int(duration)
                conf.events.append(event)

            event = Event(row['title'].strip(), id=len(conf.events)+1)
            event.room = room
            event.start = start
            event.track = track

            duration = None
            if row.get('end'):
                m2 = RE_TIME.match(row['end'])
                if m2:
                    end = datetime.replace(hour=m2[1], minute=m2[2])
                    duration = (end - start).total_seconds() // 60
            elif row.get('duration'):
                try:
                    duration = round(float(row['duration'].strip()))
                except ValueError:
                    pass
            if duration and 3 <= duration <= 120:
                event.duration = int(duration)

            for k in ('description', 'abstract', 'url', 'id', 'subtitle', 'language'):
                v = row.get(k, '').strip()
                if len(v) > 0:
                    setattr(event, k, v)

            speakerstr = row.get('speaker') or row.get('speakers')
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
