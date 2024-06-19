from .frab_xml import FrabXmlImporter
from .sessionize_json import SessionizeJsonImporter
from .conf_data import ConferenceDataImporter
from .pretalx_json import PretalxJsonImporter
from .c3voc_json import C3VocJsonImporter
from .csv import CSVImporter

importers = [
    FrabXmlImporter(),
    SessionizeJsonImporter(),
    C3VocJsonImporter(),
    PretalxJsonImporter(),
    ConferenceDataImporter(),
    CSVImporter(),
]
