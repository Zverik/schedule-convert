from .frab_xml import FrabXmlExporter
from .xcal import XCalExporter
from .ical import ICalExporter

exporters = {
    'xml': FrabXmlExporter(),
    'xcal': XCalExporter(),
    'ical': ICalExporter(),
}
