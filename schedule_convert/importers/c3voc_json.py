from ..model import Conference, Room, Speaker, Event
from datetime import datetime
import json


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

    def parse_talk(self, xevent, room):
        event = Event(xevent['title'], id=xevent.get('id'), guid=xevent.get('guid'))
        event.room = room

        event.start = datetime.fromisoformat(xevent['date'])
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

        for day in data['days']:
            for room_name, talks in day['rooms'].items():
                room = Room(room_name)
                conf.rooms.add(room)
                for talk in talks:
                    event = self.parse_talk(talk, room)
                    if event:
                        conf.events.append(event)

        return conf
