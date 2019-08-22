import datetime


class SimpleTZ(datetime.tzinfo):
    __slots__ = ('offset',)

    def __init__(self, s=None):
        self.offset = 0
        if s is None:
            pass
        elif isinstance(s, (int, float)):
            self.offset = int(s * 60)
        elif len(s) >= 2:
            if s[0] in ('−', '-'):
                mult = -1
                s = s[1:]
            else:
                if s[0] == '+':
                    s = s[1:]
                mult = 1
            hour = int(s[:2]) if s[:2].isdigit() else 0
            if len(s) >= 4:
                minute = int(s[-2:]) if s[-2:].isdigit() else 0
            else:
                minute = 0
            self.offset = mult * (hour * 60 + minute)

    def utcoffset(self, dt):
        return datetime.timedelta(minutes=self.offset)

    def dst(self, dt):
        return datetime.timedelta(0)

    def tzname(self, dt):
        if self.offset == 0:
            return 'Z'
        return '{}{:02}:{:02}'.format('+' if self.offset >= 0 else '-',
                                      abs(self.offset) // 60, self.offset % 60)

    def __repr__(self):
        return 'SimpleTZ("{}")'.format(self.tzname(None))

    def __eq__(self, other):
        if isinstance(other, SimpleTZ):
            return self.offset == other.offset
        dt = datetime.datetime(2019, 1, 1)
        return self.utcoffset(dt) == other.utcoffset(dt)


if __name__ == '__main__':
    for v in (-1, 1, '-1', '-11', '10:30', '+10:30', '+00:00', '-00:00', 'Z'):
        print('{} -> {}'.format(v, SimpleTZ(v).tzname(0)))
