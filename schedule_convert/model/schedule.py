import uuid
import re
import math
from slugify import slugify


UUID_NAMESPACE = uuid.UUID('6ba7b838-9dad-11d1-80b4-00c04fd430c8')


class Conference:
    def __init__(self, title):
        self.title = title
        self.slug = None
        self.url = None
        self.timeslot = 5
        self.days = set()
        self.rooms = set()
        self.speakers = set()
        self.events = []
        self.timezone = None
        self.default_track = None
        self.needs_data = title is None

    def __len__(self):
        return len(self.events)

    def is_empty(self):
        return len([e for e in self.events if e.active and e.start and e.room]) == 0

    def get_domain(self):
        if not self.url:
            return 'conference.com'
        m = re.search(r'://([^/]+)', self.url)
        return m.group(1)

    def make_guid(self, event):
        if self.slug is None or event.slug is None:
            return None
        if event.room is not None:
            room = event.room.name
        else:
            room = ''
        return uuid.uuid5(UUID_NAMESPACE, self.slug + event.slug +
                          room + event.start.strftime('%Y-%m-%d'))

    def filter_events(self, day=None, room=None):
        for event in sorted(self.events):
            if not event.start or not event.room or not event.active:
                continue
            if room and event.room != room:
                continue
            if day and event.start.date() != day:
                continue
            yield event

    def prepare(self):
        if self.slug is None and self.title is not None:
            self.slug = slugify(self.title)
        guids = set()
        timeslot = None
        event_ids = set()
        next_event_id = 1
        for event in self.events:
            if event.start.tzinfo is None and self.timezone is not None:
                event.start = event.start.replace(tzinfo=self.timezone)
            self.days.add(event.start.date())
            if event.id is None or str(event.id) in event_ids:
                while str(next_event_id) in event_ids:
                    next_event_id += 1
                event.id = next_event_id
            event_ids.add(str(event.id))
            if event.room:
                self.rooms.add(event.room)
            self.speakers.update(event.speakers)
            if event.slug is None:
                event.slug = slugify(event.title)
            if event.track is None:
                event.track = self.default_track
            if event.guid is None:
                event.guid = self.make_guid(event)
            if event.guid is not None:
                if event.guid in guids:
                    raise Exception('Duplicated guid {}'.format(event.guid))
                guids.add(event.guid)
            if event.duration:
                if not timeslot:
                    timeslot = event.duration
                else:
                    timeslot = math.gcd(timeslot, event.duration)
        # Deduplicate speaker ids
        speaker_ids = set()
        next_speaker_id = 1
        for sp in self.speakers:
            if sp.id is None or str(sp.id) in speaker_ids:
                while str(next_speaker_id) in speaker_ids:
                    next_speaker_id += 1
                sp.id = next_speaker_id
            speaker_ids.add(str(sp.id))
        if timeslot is not None:
            self.timeslot = timeslot

    def merge(self, other):
        if self.timeslot is None or other.timeslot < self.timeslot:
            self.timeslot = other.timeslot
        speaker_ids = set([str(sp.id) for sp in self.speakers])
        next_speaker_id = 1
        for sp in other.speakers:
            if sp.id is None or str(sp.id) in speaker_ids:
                while str(next_speaker_id) in speaker_ids:
                    next_speaker_id += 1
                sp.id = next_speaker_id
            speaker_ids.add(str(sp.id))
            self.speakers.add(sp)
        for event in other.events:
            self.events.append(event)
        self.prepare()


class Room:
    def __init__(self, name, sortId=None):
        self.name = name
        self.sortId = sortId

    def __lt__(self, other):
        if self.sortId is not None and other.sortId is not None:
            return self.sortId < other.sortId
        return self.name < other.name

    def __eq__(self, other):
        if not isinstance(other, Room):
            return False
        return self.sortId == other.sortId and self.name == other.name

    def __hash__(self):
        return hash(self.name)
