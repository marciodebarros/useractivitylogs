import logging

from flask import Response
from flask_restplus import Resource, fields
from neomodel.core import DoesNotExist

from app.api.restplus import api
from app.models import Environment

log = logging.getLogger(__name__)

ns = api.namespace('environments', description='Environment')

environment = api.model('environment', {
    'id': fields.Integer(readOnly=True, description='The internal id of the application.'),
    'server': fields.String(required=True, description='The server where the environment is deployed.'),
    'type': fields.String(required=True, description='The type of the environment (e.g.: OP, ST, MT, or DEMO).')
})

@ns.route('/')
class EnvironmentsList(Resource):

    @api.marshal_list_with(environment)
    def get(self):
        """
        Return a list with all environemnts.
        :return: list_of_environemnts
        """
        environments = Environment.nodes
        list_of_environments = list(environments)
        return list_of_environments


tenants = api.model('tenant:', {
    'id': fields.String(readOnly=True, description='The internal id of the tenant.'),
    'tenant_id': fields.String(readOnly=True, description="The name/id of the tenant.")
})


environment_tenants = api.model('environment', {
    'id': fields.Integer(readOnly=True, description='The internal id of the environment.'),
    'server': fields.String(required=True, description='The server name.'),
    'type': fields.String(requeired=True, description='The type of the environment: OP, ST, MT or DEMO'),
    'tenants': fields.Nested(tenants)
})


@ns.route('/<string:server>')
class EnvironmentTenantsList(Resource):

    @api.marshal_with(environment_tenants)
    def get(self, server):
        """
        Returns a list with all the tenants provisioned in the given environment.
        :param environment_id:
        :return:
        """
        environment = Environment.nodes.get(server=server)
        return self._get_tenants(environment)

    def _get_tenants(self, environment):
        root_environment = []
        environment_details = {'id': None, 'server': None,'type': None, 'tenants': None}
        tenant_list = []

        environment_details['id'] = environment.id
        environment_details['server'] = environment.server
        environment_details['type'] = environment.type

        environment_tenants = environment.get_all_tenants()
        for tenant in environment_tenants:
            tenant_details = {'id': tenant[0].id, 'tenant_id': tenant[0]['tenant_id']}
            tenant_list.append(tenant_details)

        environment_details['tenants'] = tenant_list
        root_environment.append(environment_details)
        return root_environment

