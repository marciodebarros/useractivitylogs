import logging.config
import asyncio

from quart import Quart, Blueprint
from goblin import Goblin


from app.config import Configuration
from app.data_loader.routes import dataloader_mod
#from app.utilities import prepare_rerun
#from app.api.endpoints.users import ns as users_namespace
#from app.api.endpoints.sessions import ns as sessions_namespace
#from app.api.endpoints.browsers import ns as browsers_namespace
#from app.api.endpoints.os import ns as os_namespace
#from app.api.endpoints.applications import ns as applications_namespace
#from app.api.endpoints.tenants import ns as tenants_namepspace
#from app.api.endpoints.devices import  ns as devices_namespace
#from app.api.endpoints.environments import ns as environments_namespace
#from app.api.endpoints.applications_instances import ns as applications_instances_namespace

#from app.api.restplus import api

from os import path

quart_app = Quart(__name__)
quart_app.config.from_object(Configuration)
quart_app.register_blueprint(dataloader_mod, url_prefix='/data_loader')

log_file_path = path.join(path.dirname(path.abspath(__file__)), 'logging.conf')
logging.config.fileConfig(log_file_path)
log = logging.getLogger(__name__)


#blueprint = Blueprint('api', __name__, url_prefix='/api')
#blueprint = Blueprint('api', __name__)

#api.init_app(blueprint)
#api.add_namespace(users_namespace)
#api.add_namespace(sessions_namespace)
#api.add_namespace(browsers_namespace)
#api.add_namespace(applications_namespace)
#api.add_namespace(tenants_namepspace)
#api.add_namespace(devices_namespace)
#api.add_namespace(os_namespace)
#api.add_namespace(environments_namespace)
#api.add_namespace(applications_instances_namespace)
#app.register_blueprint(blueprint)



