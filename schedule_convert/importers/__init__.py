from .frab_xml import FrabXmlImporter
from .sessionize_json import SessionizeJsonImporter
from .conf_data import ConferenceDataImporter
from .csv import CSVImporter

importers = [
    FrabXmlImporter(),
    SessionizeJsonImporter(),
    ConferenceDataImporter(),
    CSVImporter(),
]
