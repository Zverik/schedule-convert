from .frab_xml import FrabXmlImporter
from .sessionize_json import SessionizeJsonImporter
from .conf_data import ConferenceDataImporter
from .pretalx_json import PretalxJsonImporter
from .csv import CSVImporter

importers = [
    FrabXmlImporter(),
    SessionizeJsonImporter(),
    PretalxJsonImporter(),
    ConferenceDataImporter(),
    CSVImporter(),
]
