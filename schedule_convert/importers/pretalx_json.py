from ..model import Conference, Room, Speaker, Event
from datetime import datetime
import json


def get_string(value) -> str:
    if isinstance(value, dict):
        first_key = list(value.keys())[0]
        return value.get('en', value[first_key])
    return value


class PretalxJsonImporter:
    name = 'pretalx'

    def check(self, head):
        for k in ('talks', 'code', 'id', 'title',
                  'abstract', 'speakers', 'track', 'start'):
            if '"{}": '.format(k) not in head:
                return False
        return True

    def parse(self, fileobj):
        data = json.load(fileobj)
        conf = Conference(None)

        speakers = {}
        for xspeaker in data['speakers']:
            name = xspeaker['name']
            speaker = Speaker(name, id=xspeaker['code'])
            speaker.photo = xspeaker.get('avatar')
            speakers[speaker.id] = speaker

        rooms = {}
        for xroom in data['rooms']:
            room = Room(get_string(xroom['name']), sortId=xroom['id'])
            rooms[xroom['id']] = room

        for xevent in data['talks']:
            event = Event(get_string(xevent['title']), id=xevent['id'])
            event.room = rooms[xevent['room']]
            event.start = datetime.fromisoformat(xevent['start'])
            if 'duration' in xevent:
                event.duration = xevent['duration']
            else:
                end = datetime.fromisoformat(xevent['end'])
                event.duration = round((end - event.start).total_seconds() / 60)
            event.slug = xevent.get('code', f'e{event.id}')
            if 'abstract' in xevent:
                event.description = xevent['abstract'].replace('\x0D', '')
            for sp in xevent.get('speakers', []):
                event.speakers.append(speakers[sp])
            conf.events.append(event)
        return conf
