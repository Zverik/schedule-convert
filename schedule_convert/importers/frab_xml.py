from ..model import Conference, Room, Speaker, Event, SimpleTZ
import re
import logging
from datetime import date, datetime
try:
    from lxml import etree
except ImportError:
    import xml.etree.ElementTree as etree


RE_DATE = re.compile(r'(\d{4})-(\d\d)-(\d\d)')
RE_MINUTE = re.compile(r'^(\d+):(\d+)(?: ([AP]M))?$')
RE_TIMEZONE = re.compile(r'\d\d:?\d\d(Z|[+-]\d\d:?\d\d)')
DATE_ISO_FORMAT = '%Y-%m-%dT%H:%M:%S%z'


def from_minutes(dur):
    if dur is None:
        return None
    if ':' in dur:
        parts = [int(x) for x in dur.split(':')]
        return parts[0] * 60 + parts[1]
    return round(float(dur))


def parse_time_with_day(timestr, day):
    m = RE_MINUTE.match(timestr)
    if m:
        hour = int(m.group(1))
        if m.group(3) == 'PM' and hour < 12:
            hour += 12
        elif m.group(3) == 'AM' and hour == 12:
            hour = 0
        return datetime(day.year, day.month, day.day,
                        hour, int(m.group(2)))
    if 'T' in timestr:
        return datetime.strptime(timestr, DATE_ISO_FORMAT)
    raise ValueError('Unknown format: {}'.format(timestr))


def find_timezone(timestr):
    m = RE_TIMEZONE.search(timestr)
    if m:
        return SimpleTZ(m.group(1))
    return None


def getttext(root, tag):
    n = root.find(tag)
    if n is None or n.text is None:
        return None
    return n.text.strip()


class FrabXmlImporter:
    name = 'xml'

    def check(self, head):
        for k in ('conference', 'day', 'title', 'room', 'event',
                  'start', 'end'):
            if '<'+k not in head:
                return False
        return True

    def parse(self, fileobj):
        root = etree.parse(fileobj).getroot()
        xconf = root.find('conference')
        conf = Conference(getttext(xconf, 'title'))
        conf.timeslot = from_minutes(getttext(xconf, 'timeslot_duration'))
        conf.slug = getttext(xconf, 'acronym')
        conf.url = getttext(xconf, 'base_url') or getttext(xconf, 'baseurl')
        speakers = {}
        for xday in root.findall('day'):
            m = RE_DATE.match(xday.get('date'))
            day = date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
            conf.days.add(day)
            for xroom in xday.findall('room'):
                room = Room(xroom.get('name'))
                conf.rooms.add(room)
                for xevent in xroom.findall('event'):
                    title = getttext(xevent, 'title')
                    event = Event(title, id=xevent.get('id'), guid=xevent.get('guid'))
                    event.room = room
                    event.start = parse_time_with_day(getttext(xevent, 'start'), day)
                    if xevent.find('date') is not None:
                        timezone = find_timezone(getttext(xevent, 'date'))
                        if not conf.timezone:
                            conf.timezone = timezone
                        elif timezone != conf.timezone:
                            logging.warning(
                                'Error: timezone %s in %s differs from last timezone %s',
                                timezone, getttext(xevent, 'date'), conf.timezone)
                    duration = getttext(xevent, 'duration')
                    if not duration:
                        continue
                    event.duration = from_minutes(duration)
                    event.subtitle = getttext(xevent, 'subtitle')
                    event.slug = getttext(xevent, 'slug')
                    event.url = getttext(xevent, 'url')
                    event.subtitle = getttext(xevent, 'subtitle')
                    rec = xevent.find('recording')
                    if rec is None:
                        event.license = None
                        event.can_record = True
                    else:
                        event.license = getttext(rec, 'license')
                        event.can_record = getttext(rec, 'optout') != 'true'
                    event.language = getttext(xevent, 'language')
                    event.track = getttext(xevent, 'track')
                    event.abstract = getttext(xevent, 'abstract')
                    event.description = getttext(xevent, 'description')
                    for xperson in xevent.find('persons'):
                        person_id = xperson.get('id')
                        if person_id not in speakers:
                            speakers[person_id] = Speaker(xperson.text, id=person_id)
                        event.speakers.append(speakers[person_id])
                    conf.events.append(event)
        return conf
