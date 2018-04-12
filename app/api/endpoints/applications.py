import logging

from flask import Response
from flask_restplus import Resource, fields
from neomodel.core import DoesNotExist

from app.api.restplus import api
from app.models import Application

log = logging.getLogger(__name__)

ns = api.namespace('applications', description='Application')

application = api.model('application', {
    'id': fields.Integer(readOnly=True, description='The internal id of the application.'),
    'name': fields.String(required=True, description='The name of the appication represented by the logical id (LID) prefix.')
})


@ns.route('/')
class ApplicationsList(Resource):

    @api.marshal_list_with(application)
    @api.doc(model=application)
    def get(self):
        """
        Return a list with all applications.
        :return: list_of_applications
        """
        applications = Application.nodes
        list_of_applications = list(applications)
        return list_of_applications


screens = api.model('screen:', {
    'id': fields.String(readOnly=True, description='The internal id of the screen.'),
    'name': fields.String(readOnly=True, description="The name of the screen.")
})


application_screens = api.model('application', {
    'id': fields.Integer(readOnly=True, description='The internal id of the application.'),
    'name': fields.String(required=True, description='The logical id (LID) of the applicaiton.'),
    'screens': fields.Nested(screens)
})



@ns.route('/<path:name>')
class ApplicationScreensList(Resource):
    @api.marshal_with(application_screens)
    @api.doc(model=application_screens)
    def get(self, name):
        """
        Return a list with all the screens associated with the given application.
        :parameter name
        :return application_screens
        """
        application = Application.nodes.get(name=name)
        return self._get_screens(application)

    def _get_screens(self, application):
        root_application = []
        application_details = {'id': None,'name': None, 'screens': None}
        screen_list = []

        application_details['id'] = application.id
        application_details['name'] = application.name

        application_screens = application.get_all_screens()
        for screen in application_screens:
            screen_details = {'id': screen[0].id, 'name': screen[0]['name']}
            screen_list.append(screen_details)

        application_details['screens'] = screen_list
        root_application.append(application_details)
        return root_application