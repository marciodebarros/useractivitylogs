import logging

from flask import Response
from flask_restplus import Resource, fields
from neomodel.core import DoesNotExist

from app.api.restplus import api
from app.models import Device

log = logging.getLogger(__name__)

ns = api.namespace('devices', description='Device')

device = api.model('device', {
    'id': fields.Integer(readOnly=True, description='The internal id of the application.'),
    'family': fields.String(required=True, description='The family (e.g.: iOS, Android, Windowss, etc...) of the device.'),
    'brand': fields.String(required=True, description='The brand of the device.'),
    'model': fields.String(required=True, description='The model of the device.'),
    'type': fields.String(required=True, description='The type of the device.'),
    'is_touch_capable': fields.Boolean(required=True, description='Indicates if the device is touch capable.')
})

@ns.route('/')
class DevicesList(Resource):

    @api.marshal_list_with(device)
    def get(self):
        """
        Return a list with all devices.
        :return: list_of_devices
        """
        devices = Device.nodes
        list_of_devices = list(devices)
        return list_of_devices
