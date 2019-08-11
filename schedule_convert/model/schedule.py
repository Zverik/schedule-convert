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
        for event in self.events:
            self.days.add(event.start.date())
            if event.room:
                self.rooms.add(event.room)
            self.speakers.update(event.speakers)

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
