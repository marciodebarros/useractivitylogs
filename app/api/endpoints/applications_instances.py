import logging

from flask import Response
from flask_restplus import Resource, fields
from neomodel.core import DoesNotExist

from app.api.restplus import api
from app.models import ApplicationInstance

log = logging.getLogger(__name__)

ns = api.namespace('applications_instances', description='Applications Instances')

application_instance = api.model('applications_instances', {
    'id': fields.Integer(readOnly=True, description='The internal id of the application.'),
    'application_id': fields.String(required=True, description='The id of the appication instance represented by the logical id (LID).')
})


@ns.route('/')
class ApplicationsInstanceList(Resource):

    @api.marshal_list_with(application_instance)
    @api.doc(model=application_instance)
    def get(self):
        """
        Return a list with all applications.
        :return: list_of_applications
        """
        application_instance = ApplicationInstance.nodes
        list_of_application_instances = list(application_instance)
        return list_of_application_instances


screens = api.model('screen_instance:', {
    'id': fields.String(readOnly=True, description='The internal id of the screen.'),
    'screen_id': fields.String(readOnly=True, description="The name of the screen.")
})


application_screens = api.model('applications_instances', {
    'id': fields.Integer(readOnly=True, description='The internal id of the application.'),
    'application_id': fields.String(required=True, description='The logical id (LID) of the applicaiton.'),
    'screens_instances': fields.Nested(screens)
})



@ns.route('/<path:application_id>')
class ApplicationInstanceScreensList(Resource):
    @api.marshal_with(application_screens)
    @api.doc(model=application_screens)
    def get(self, application_id):
        """
        Return a list with all the screens instances associated with the given application instance.
        :parameter name
        :return application_screens
        """
        application_instance = ApplicationInstance.nodes.get(application_id=application_id)
        return self._get_screens(application_instance)

    def _get_screens(self, application_instance):
        root_application_instance = []
        application_instance_details = {'id': None,'application_id': None, 'screens_instances': None}
        screen_instances_list = []

        application_instance_details['id'] = application_instance.id
        application_instance_details['application_id'] = application_instance.application_id

        application_instance_screens = application_instance.get_all_screens()
        for screen_instance in application_instance_screens:
            screen_instances_details = {'id': screen_instance[0].id, 'screen_id': screen_instance[0]['screen_id']}
            screen_instances_list.append(screen_instances_details)

        application_instance_details['screens_instances'] = screen_instances_list
        root_application_instance.append(application_instance_details)
        return root_application_instance