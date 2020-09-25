import json
import os

import yaml
from flask import Blueprint, render_template

from logic import Constants


def construct_blueprint(settings, version):
    routes = Blueprint('routes', __name__)

    @routes.route('/', methods=['GET'])
    def index():
        yamlPath = os.path.join(Constants.ROOT_DIR, 'docs', 'api.yml')
        with open(yamlPath, 'r') as yamlFile:
            specification = yaml.load(yamlFile, Loader=yaml.FullLoader)

        specification['servers'][0]['url'] = settings['api']['url']
        specification['info']['version'] = version['name']

        specification = json.dumps(specification)
        return render_template('api.html',
                               appName=Constants.APP_NAME,
                               openApiSpecification=specification)

    return routes
