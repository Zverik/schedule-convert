import re
import datetime
try:
    from lxml import etree
except ImportError:
    import xml.etree.ElementTree as etree


XCAL_URN = 'urn:ietf:params:xml:ns:xcal'
PENTABARF_URN = 'http://pentabarf.org'
PENTABARF_NS = '{' + PENTABARF_URN + '}'
NSMAP = {
    None: XCAL_URN,
    'pentabarf': PENTABARF_URN
}
DATE_FORMAT = '%Y%m%dT%H%M%S'


class XCalExporter:
    extension = 'xcal'

    def write(self, fileobj, conf):
        root = etree.Element('iCalendar', nsmap=NSMAP)
        vc = etree.SubElement(root, 'vcalendar')
        etree.SubElement(vc, 'version').text = '2.0'
        etree.SubElement(vc, 'prodid').text = '-//Pentabarf//Schedule//EN'
        etree.SubElement(vc, 'x-wr-caldesc').text = conf.title
        etree.SubElement(vc, 'x-wr-calname').text = conf.title
        if not conf.url:
            domain = 'conference.com'
        else:
            m = re.search(r'://([^/]+)', conf.url)
            domain = m.group(1)

        for event in sorted(conf.events):
            if not event.active or not event.room:
                continue
            xevent = etree.SubElement(vc, 'vevent')
            etree.SubElement(xevent, 'method').text = 'PUBLISH'
            etree.SubElement(xevent, 'uid').text = event.slug + '@@' + domain

            etree.SubElement(xevent, PENTABARF_NS + 'event-id').text = str(event.guid)
            etree.SubElement(xevent, PENTABARF_NS + 'event-slug').text = event.slug
            etree.SubElement(xevent, PENTABARF_NS + 'title').text = event.title
            etree.SubElement(xevent, PENTABARF_NS + 'subtitle').text = event.subtitle
            etree.SubElement(xevent, PENTABARF_NS + 'language').text = event.language
            etree.SubElement(xevent, PENTABARF_NS + 'language-code').text = event.language

            duration = datetime.timedelta(minutes=event.duration)
            etree.SubElement(xevent, 'dtstart').text = event.start.strftime(DATE_FORMAT)
            etree.SubElement(xevent, 'dtend').text = (event.start + duration).strftime(DATE_FORMAT)
            etree.SubElement(xevent, 'duration').text = str(event.duration / 60.0)

            etree.SubElement(xevent, 'summary').text = event.title
            etree.SubElement(xevent, 'description').text = event.description or ''
            etree.SubElement(xevent, 'class').text = 'PUBLIC'
            etree.SubElement(xevent, 'status').text = 'CONFIRMED'
            etree.SubElement(xevent, 'category').text = 'Talk'
            etree.SubElement(xevent, 'url').text = event.url or ''
            etree.SubElement(xevent, 'location').text = event.room.name
            for sp in event.speakers:
                etree.SubElement(xevent, 'attendee').text = sp.name
        result = etree.tostring(root, xml_declaration=True, encoding='utf-8', pretty_print=True)
        fileobj.write(result.decode('utf-8'))
