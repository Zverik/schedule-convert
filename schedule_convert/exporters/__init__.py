from .frab_xml import FrabXmlExporter
from .xcal import XCalExporter

exporters = {
    'xml': FrabXmlExporter(),
    'xcal': XCalExporter(),
}
