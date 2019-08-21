import uuid


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
        self.needs_data = title is None

    def make_guid(self, event):
        if self.slug is None or event.slug is None:
            return None
        if event.room is not None:
            room = event.room.name
        else:
            room = ''
        return uuid.uuid5(UUID_NAMESPACE, self.slug + event.slug +
                          room + event.start.strftime('%Y-%m-%d'))

    def slugify(self, s):
        if s is None:
            return None
        return s.lower().strip().replace(' ', '_')

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
            self.slug = self.slugify(self.title)
        guids = set()
        for event in self.events:
            self.days.add(event.start.date())
            if event.room:
                self.rooms.add(event.room)
            self.speakers.update(event.speakers)
            if event.slug is None:
                event.slug = self.slugify(event.title)
            if event.guid is None:
                event.guid = self.make_guid(event)
            if event.guid is not None:
                if event.guid in guids:
                    raise Exception('Duplicated guid {}'.format(event.guid))
                guids.add(event.guid)

    def merge(self, other):
        if other.timeslot < self.timeslot:
            self.timeslot = other.timeslot
        speaker_ids = set(speaker.id for speaker in self.speakers)
        next_id = 1
        for sp in other.speakers:
            if sp.id in speaker_ids:
                while str(next_id) in speaker_ids:
                    next_id += 1
                sp.id = next_id
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
        return self.sortId == other.sortId and self.name == other.name

    def __hash__(self):
        return hash(self.name)
