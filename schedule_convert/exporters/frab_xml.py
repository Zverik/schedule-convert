from datetime import timedelta
try:
    from lxml import etree
except ImportError:
    import xml.etree.ElementTree as etree


DATE_FORMAT = '%Y-%m-%d'
DATE_ISO_FORMAT = '%Y-%m-%dT%H:%M:%S'


def to_minutes(duration):
    hours = duration // 60
    minutes = duration % 60
    return '{:02d}:{:02d}'.format(hours, minutes)


def to_timestamp(date):
    if date.tzinfo is None:
        return date.strftime(DATE_ISO_FORMAT)
    return date.strftime(DATE_ISO_FORMAT) + date.tzinfo.tzname(date)


class FrabXmlExporter:
    extension = 'xml'

    def write(self, fileobj, conf):
        root = etree.Element('schedule')
        etree.SubElement(root, 'version').text = '0.2'
        xconf = etree.SubElement(root, 'conference')
        etree.SubElement(xconf, 'acronym').text = conf.slug
        etree.SubElement(xconf, 'title').text = conf.title
        etree.SubElement(xconf, 'start').text = min(conf.days).strftime(DATE_FORMAT)
        etree.SubElement(xconf, 'end').text = max(conf.days).strftime(DATE_FORMAT)
        etree.SubElement(xconf, 'days').text = str(len(conf.days))
        etree.SubElement(xconf, 'timeslot_duration').text = to_minutes(conf.timeslot)
        etree.SubElement(xconf, 'base_url').text = conf.url or ''

        for i, day in enumerate(sorted(conf.days)):
            all_talks = list(conf.filter_events(day=day))
            if not all_talks:
                continue
            xday = etree.SubElement(root, 'day')
            xday.set('index', str(i+1))
            xday.set('date', day.strftime(DATE_FORMAT))
            xday.set('start', to_timestamp(all_talks[0].start))
            xday.set('end', to_timestamp(all_talks[-1].start + timedelta(
                minutes=all_talks[-1].duration)))
            for room in sorted(conf.rooms):
                xroom = None
                for talk in conf.filter_events(day=day, room=room):
                    if xroom is None:
                        xroom = etree.SubElement(xday, 'room')
                        xroom.set('name', room.name)
                    xtalk = etree.SubElement(xroom, 'event')
                    xtalk.set('guid', str(talk.guid))
                    xtalk.set('id', str(talk.id))
                    etree.SubElement(xtalk, 'date').text = to_timestamp(talk.start)
                    etree.SubElement(xtalk, 'start').text = talk.start.strftime('%H:%M')
                    etree.SubElement(xtalk, 'duration').text = to_minutes(talk.duration)
                    etree.SubElement(xtalk, 'room').text = room.name
                    etree.SubElement(xtalk, 'slug').text = talk.slug
                    etree.SubElement(xtalk, 'url').text = talk.url or ''
                    rec = etree.SubElement(xtalk, 'recording')
                    etree.SubElement(rec, 'license').text = ''
                    etree.SubElement(rec, 'optout').text = 'false' if talk.can_record else 'true'
                    etree.SubElement(xtalk, 'title').text = talk.title
                    etree.SubElement(xtalk, 'subtitle').text = talk.subtitle or ''
                    etree.SubElement(xtalk, 'track').text = talk.track or ''
                    etree.SubElement(xtalk, 'type').text = 'Talk'
                    etree.SubElement(xtalk, 'language').text = talk.language
                    etree.SubElement(xtalk, 'abstract').text = talk.abstract or ''
                    etree.SubElement(xtalk, 'description').text = talk.description or ''
                    etree.SubElement(xtalk, 'logo').text = talk.logo or ''
                    persons = etree.SubElement(xtalk, 'persons')
                    for speaker in talk.speakers:
                        xsp = etree.SubElement(persons, 'person')
                        xsp.set('id', str(speaker.id))
                        xsp.text = speaker.name
                    etree.SubElement(xtalk, 'links')
                    etree.SubElement(xtalk, 'attachments')
        try:
            result = etree.tostring(root, encoding='unicode', pretty_print=True)
        except TypeError:
            # built-in ElementTree doesn't do pretty_print
            result = etree.tostring(root, encoding='unicode')
        fileobj.write("<?xml version='1.0' encoding='utf-8'?>\n")
        fileobj.write(result)
