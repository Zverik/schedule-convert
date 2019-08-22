from ..model import SimpleTZ
from datetime import datetime, timedelta
try:
    import vobject
except ImportError:
    pass


class ICalExporter:
    extension = 'ics'

    def write(self, fileobj, conf):
        now = datetime.now(SimpleTZ())
        domain = conf.get_domain()
        cal = vobject.iCalendar()
        cal.add('prodid').value = '-//pretalx//{}//'.format(domain)
        for event in sorted(conf.events):
            if not event.active or not event.room:
                continue
            vevent = cal.add('vevent')
            speakers = ', '.join(sp.name for sp in event.speakers)
            vevent.add('summary').value = '{} — {}'.format(event.title, speakers)
            vevent.add('dtstamp').value = now
            vevent.add('location').value = event.room.name
            vevent.add('uid').value = 'pretalx-{}-{}@{}'.format(
                conf.slug, event.guid, domain)
            vevent.add('dtstart').value = event.start
            vevent.add('dtend').value = event.start + timedelta(minutes=event.duration)
            vevent.add('description').value = event.abstract or event.description or ''
            if event.url:
                vevent.add('url').value = event.url
        fileobj.write(cal.serialize())
