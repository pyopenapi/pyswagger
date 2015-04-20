from ..consts import FILE_TYPE_JSON, FILE_TYPE_YAML

SCHEMA_APIS = 'apis'
SCHEMA_PATH = 'path'

FILE_EXT_JSON = 'json'
FILE_EXT_YAML = 'yaml'
SWAGGER_FILE_NAMES = [
    'resource_list' + '.' + FILE_EXT_JSON,
    'swagger' + '.' + FILE_EXT_JSON,
    'swagger' + '.' + FILE_EXT_YAML,
]

EXT_MAPPING = {
    FILE_TYPE_JSON: FILE_EXT_JSON,
    FILE_TYPE_YAML: FILE_EXT_YAML
}

SCOPE_SEPARATOR = '!##!'
