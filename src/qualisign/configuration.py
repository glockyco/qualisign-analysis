from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

DATABASES = {
    "dev": {
        "NAME": "postgres",
        "USER": "postgres",
        "PASSWORD": "postgres",
        "HOST": "127.0.0.1",
        "PORT": 5432,
    },
}

DB = DATABASES["dev"]

ENGINE_STRING = "postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}".format(
    user=DB["USER"],
    password=DB["PASSWORD"],
    host=DB["HOST"],
    port=DB["PORT"],
    database=DB["NAME"],
)

ENGINE: Engine = create_engine(ENGINE_STRING)
PROJECT_FEATURES_TABLE = "mv_projects_features"
PACKAGE_FEATURES_TABLE = "mv_pakkages_features"
CLASS_FEATURES_TABLE = "mv_clazzes_features"

QUALITY_ATTRIBUTES = [
    "effectiveness",
    "extendibility",
    "flexibility",
    "functionality",
    "reusability",
    "understandability",
]

QUALITY_ATTRIBUTE_NAMES = {
    "effectiveness": "Effectiveness",
    "extendibility": "Extendibility",
    "flexibility": "Flexibility",
    "functionality": "Functionality",
    "reusability": "Reusability",
    "understandability": "Understandability",
}

QMOOD_METRICS = [
    "ana",
    "cam",
    "cis",
    "dam",
    "dcc",
    "dsc",
    "mfa",
    "moa",
    "noh",
    "nom",
    "nop",
]

QMOOD_METRICS_NAMES = {
    "ana": "ANA",
    "cam": "CAM",
    "cis": "CIS",
    "dam": "DAM",
    "dcc": "DCC",
    "dsc": "DSC",
    "mfa": "MFA",
    "moa": "MOA",
    "noh": "NOH",
    "nom": "NOM",
    "nop": "NOP",
}

MISC_METRICS = [
    "amc",
    "ca",
    "cbm",
    "cc",
    "ce",
    "ic",
    "lcom",
    "lcom3",
    "loc",
    "noc",
    "rfc",
    "wmc",
]

MISC_METRICS_NAMES = {
    "amc": "AMC",
    "ca": "CA",
    "cbm": "CBM",
    "cc": "CC",
    "ce": "CE",
    "ic": "IC",
    "lcom": "LCOM",
    "lcom3": "LCOM3",
    "loc": "LOC",
    "noc": "NOC",
    "rfc": "RFC",
    "wmc": "WMC",
}

FEATURES = QUALITY_ATTRIBUTES + QMOOD_METRICS + MISC_METRICS

FEATURE_NAMES = {**QUALITY_ATTRIBUTE_NAMES, **QMOOD_METRICS_NAMES, **MISC_METRICS_NAMES}

DESIGN_PATTERNS = [
    "adapter",
    "bridge",
    "chain_of_responsibility",
    "command",
    "composite",
    "decorator",
    "factory_method",
    "observer",
    "prototype",
    "proxy",
    "proxy2",
    "singleton",
    "state",
    "strategy",
    "template_method",
    "visitor",
]

DESIGN_PATTERN_NAMES = {
    "adapter": "Adapter",
    "bridge": "Bridge",
    "chain_of_responsibility": "Chain of Responsibility",
    "command": "Command",
    "composite": "Composite",
    "decorator": "Decorator",
    "factory_method": "Factory Method",
    "observer": "Observer",
    "prototype": "Prototype",
    "proxy": "Proxy",
    "proxy2": "Proxy2",
    "singleton": "Singleton",
    "state": "State",
    "strategy": "Strategy",
    "template_method": "Template Method",
    "visitor": "Visitor",
}
