from .frab_xml import FrabXmlImporter
from .sessionize_json import SessionizeJsonImporter
from .conf_data import ConferenceDataImporter

importers = [
    FrabXmlImporter(),
    SessionizeJsonImporter(),
    ConferenceDataImporter(),
]
