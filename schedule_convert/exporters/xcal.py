try:
    from lxml import etree
except ImportError:
    import xml.etree.ElementTree as etree


class XCalExporter:
    extension = 'xcal'

    def write(self, fileobj, conf):
        root = etree.Element('iCalendar')
        vc = etree.SubElement(root, 'vcalendar')
        etree.SubElement(vc, 'version').text = '2.0'
        etree.SubElement(vc, 'prodid').text = '-//Pentabarf//Schedule//EN'
        etree.SubElement(vc, 'x-wr-caldesc').text = conf.title
        etree.SubElement(vc, 'x-wr-calname').text = conf.title
        for event in sorted(conf.events):
            if not event.active or not event.room:
                continue
            xevent = etree.SubElement(vc, 'vevent')
            etree.SubElement(xevent, 'method').text = 'PUBLISH'
            # TODO: https://github.com/pretalx/pretalx/blob/master/src/pretalx/agenda/templates/agenda/schedule.xcal
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
