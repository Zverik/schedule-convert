from ..model import Conference, SimpleTZ
from io import TextIOWrapper


class ConferenceDataImporter:
    def check(self, head):
        keys = [l.split('=')[0].strip() for l in head.splitlines()]
        for k in ('title', 'slug', 'url'):
            if k not in keys:
                return False
        return True

    def parse(self, fileobj):
        data = {}
        for line in TextIOWrapper(fileobj, 'utf-8'):
            kv = line.split('=')
            if len(kv) == 2:
                data[kv[0].strip()] = kv[1].strip()
        conf = Conference(data['title'])
        conf.slug = data['slug']
        conf.url = data['url']
        if 'timezone' in data:
            conf.timezone = SimpleTZ(data['timezone'])
        if 'timeslot' in data:
            conf.timeslot = int(data['timeslot'])
        if 'track' in data:
            conf.default_track = data['track']
        return conf
