import json

with open('../settings.json', 'r', encoding='UTF-8') as f:
    SETTINGS = json.load(f)

with open('version.json', 'r', encoding='UTF-8') as f:
    VERSION = json.load(f)['version']
