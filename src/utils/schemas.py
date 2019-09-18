import yaml
import os

_PATH = 'src/server/schemas/'


def load_schemas():
    schemas = {}
    for name in os.listdir(_PATH):
        path = os.path.join(_PATH, name)
        basename = os.path.splitext(name)[0]
        with open(path) as fd:
            schema = yaml.safe_load(fd.read())
            schemas[basename] = schema
    return schemas
