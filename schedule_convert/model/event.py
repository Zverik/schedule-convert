import uuid


class Event:
    def __init__(self, title, id=0, guid=None):
        self.title = title
        self.subtitle = None
        self.abstract = None
        self.description = None
        self.duration = 0
        self.start = None
        self.room = None
        self.track = None
        self.id = id
        if guid is None or isinstance(guid, uuid.UUID):
            self.guid = guid
        else:
            try:
                self.guid = uuid.UUID(guid)
            except ValueError:
                self.guid = None
        self.speakers = []
        self.license = None
        self.can_record = True
        self.active = True
        self.language = 'en'
        self.url = None
        self.logo = None
        self.slug = None

    def __lt__(self, other):
        return self.start < other.start
