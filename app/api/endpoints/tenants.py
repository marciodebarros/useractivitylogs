import logging

from flask import Response
from flask_restplus import Resource, fields
from neomodel.core import DoesNotExist

from app.api.restplus import api
from app.models import Tenant

log = logging.getLogger(__name__)

ns = api.namespace('tenants', description='Tenant')

tenant = api.model('tenant', {
    'id': fields.Integer(readOnly=True, description='The internal id of the tenant.'),
    'tenant_id': fields.String(required=True, description='The tenant id.'),
})

@ns.route('/')
class TenantsList(Resource):

    @api.marshal_list_with(tenant)
    def get(self):
        """
        Return a list with all tenants.
        :return: list_of_tenants
        """
        tenants = Tenant.nodes
        list_of_tenants = list(tenants)
        return list_of_tenants
