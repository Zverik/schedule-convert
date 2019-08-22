from ..model import Conference, Room, Speaker, Event
from datetime import datetime
import json


DATE_ISO_FORMAT = '%Y-%m-%dT%H:%M:%S'


def parse_time(timestr):
    if 'T' in timestr:
        return datetime.strptime(timestr, DATE_ISO_FORMAT)
    raise ValueError('Unknown format: {}'.format(timestr))


class SessionizeJsonImporter:
    name = 'sessionize'

    def check(self, head):
        for k in ('sessions', 'id', 'title', 'startsAt',
                  'isServiceSession', 'roomId'):
            if '"{}": '.format(k) not in head:
                return False
        return True

    def parse(self, fileobj):
        data = json.load(fileobj)
        conf = Conference(None)
        speakers = {}
        for xspeaker in data['speakers']:
            name = xspeaker['fullName']
            speaker = Speaker(name, id=xspeaker['id'])
            speaker.job = xspeaker['tagLine']
            speaker.bio = xspeaker['bio']
            speaker.featured = xspeaker['isTopSpeaker']
            speaker.photo = xspeaker['profilePicture']
            speakers[speaker.id] = speaker
        rooms = {}
        for xroom in data['rooms']:
            room = Room(xroom['name'], sortId=xroom['sort'])
            rooms[xroom['id']] = room
        for xevent in data['sessions']:
            event = Event(xevent['title'], id=xevent['id'])
            event.room = rooms[xevent['roomId']]
            event.start = parse_time(xevent['startsAt'])
            event.duration = round((parse_time(xevent['endsAt'])
                                    - event.start).total_seconds() / 60)
            event.slug = 'e{}'.format(event.id)
            event.description = xevent['description'].replace('\x0D', '')
            for sp in xevent['speakers']:
                event.speakers.append(speakers[sp])
            conf.events.append(event)
        return conf
