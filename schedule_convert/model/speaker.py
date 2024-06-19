class Speaker:
    def __init__(self, name, id=None):
        self.id = id
        self.name = name
        self.code = None
        self.job = None
        self.bio = None
        self.featured = False
        self.url = None
        self.photo = None

    def __eq__(self, other):
        if not isinstance(other, Speaker):
            return False
        if self.id is not None and other.id is not None:
            return self.id == other.id
        return self.name == other.name

    def __hash__(self):
        return hash(self.name) + hash(self.id or 0)
