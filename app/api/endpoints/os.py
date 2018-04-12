import logging

from flask import Response
from flask_restplus import Resource, fields
from neomodel.core import DoesNotExist

from app.api.restplus import api
from app.models import OS

log = logging.getLogger(__name__)

ns = api.namespace('os', description='OS')

os = api.model('os', {
    'id': fields.Integer(readOnly=True, description='The internal id of of an OS.'),
    'family': fields.String(required=True, description='The family of the OS.'),
    'version': fields.String(required=True, description='The version of the OS.')
})

# TODO - Define endpoints that return sessions that started, ended and timedout in a date/time range, used a given ip address
@ns.route('/')
class SessionsList(Resource):

    @api.marshal_list_with(os)
    def get(self):
        """
        Return a list with all OSs
        :return: list_of_os
        """
        oss = OS.nodes
        list_of_os = list(oss)
        return list_of_os

