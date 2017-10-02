from flask import blueprints

instance = blueprints.Blueprint('web', 'web')

from . import index