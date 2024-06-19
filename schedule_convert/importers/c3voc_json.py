from ..model import Conference, Room, Speaker, Event, SimpleTZ
from datetime import date, datetime
import json
import re


RE_DATE = re.compile(r'(\d{4})-(\d\d)-(\d\d)')
RE_MINUTE = re.compile(r'^(\d+):(\d+)(?: ([AP]M))?$')
RE_TIMEZONE = re.compile(r'\d\d:?\d\d(Z|[+-]\d\d:?\d\d)')


class C3VocJsonImporter:
    name = 'pretalx'

    def check(self, head):
        return '"$schema": "https://c3voc.de/schedule/schema.json"' in head

    def from_minutes(self, dur):
        if dur is None:
            return None
        if ':' in dur:
            parts = [int(x) for x in dur.split(':')]
            return parts[0] * 60 + parts[1]
        return round(float(dur))

    def parse_time_with_day(self, timestr, day):
        m = RE_MINUTE.match(timestr)
        if m:
            hour = int(m.group(1))
            if m.group(3) == 'PM' and hour < 12:
                hour += 12
            elif m.group(3) == 'AM' and hour == 12:
                hour = 0
            return datetime(day.year, day.month, day.day,
                            hour, int(m.group(2)))
        if 'T' in timestr:
            return datetime.fromisoformat(timestr)
        raise ValueError('Unknown format: {}'.format(timestr))

    def find_timezone(self, timestr):
        m = RE_TIMEZONE.search(timestr)
        if m:
            return SimpleTZ(m.group(1))
        return None

    def parse_talk(self, xevent, day, room):
        event = Event(xevent['title'], id=xevent.get('id'),
                      guid=xevent.get('guid'))
        event.room = room

        event.start = self.parse_time_with_day(xevent['start'], day)
        # event.start = datetime.fromisoformat(xevent['date'])
        duration = xevent.get('duration')
        if not duration:
            return None
        event.duration = self.from_minutes(duration)

        event.subtitle = xevent.get('subtitle')
        event.slug = xevent.get('slug')
        event.url = xevent.get('url')
        event.feedback_url = xevent.get('feedback_url')
        event.language = xevent.get('language')
        event.track = xevent.get('track')
        event.abstract = xevent.get('abstract')
        event.description = xevent.get('description')
        event.can_record = not xevent.get('do_not_record', False)
        event.license = xevent.get('recording_license')

        for sp in xevent.get('persons', []):
            speaker = Speaker(sp['public_name'], id=sp['code'])
            speaker.code = sp.get('code')
            speaker.bio = sp.get('biography')
            speaker.photo = sp.get('avatar')
            event.speakers.append(speaker)
        return event

    def parse(self, fileobj):
        data_glob = json.load(fileobj)
        data = data_glob['schedule']['conference']
        conf = Conference(data['title'])
        conf.url = data_glob['schedule'].get('url')
        conf.slug = data.get('acronym')
        conf.timeslot = self.from_minutes(data.get('timeslot_duration'))

        for xday in data['days']:
            m = RE_DATE.match(xday.get('date'))
            day = date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
            conf.days.add(day)
            for room_name, talks in xday['rooms'].items():
                room = Room(room_name)
                conf.rooms.add(room)
                for talk in talks:
                    event = self.parse_talk(talk, day, room)
                    if event:
                        conf.events.append(event)

        return conf
