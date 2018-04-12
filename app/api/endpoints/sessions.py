import logging

from flask import Response
from flask_restplus import Resource, fields
from neomodel.core import DoesNotExist

from app.api.restplus import api, base_reponse
from app.models import Session

log = logging.getLogger(__name__)

ns = api.namespace('sessions', description='Sessions')

session = api.model('session',  {
    'id': fields.Integer(readOnly=True, description='The internal id of of a session.'),
    'session_id': fields.String(required=True, description='The session id.'),
    'ip_address': fields.String(required=True, description='A list of IP addresses '
                                                           'used during the session.'),
    'start': fields.DateTime(required=True, description='The date and time when the session '
                                                        'started.'),
    'end': fields.DateTime(required=True, description='The date and time when the session ended.'),
    'timeout': fields.DateTime(required=True, description='The date and time when the session timedout.')
})

# TODO - Define endpoints that return sessions that started, ended and timedout in a date/time range, used a given ip address
@ns.route('/')
class SessionsList(Resource):

    @api.marshal_list_with(session)
    def get(self):
        """
        Return a list with all sessions
        :return: list_of_sessions
        """
        try:
            sessions = Session.nodes
            list_of_sessions = list(sessions)
            limit = 120
            return list_of_sessions
        except DoesNotExist:
            return Response(('{"No Content": "No session nodes found"}'), status = 200, mimetype='application/json')

@ns.route('/<string:session_id>')
class SessionItem(Resource):

    @api.marshal_with(session)
    def get(self, session_id):
        """
        Return a session with the given session_id
        :param session_id: session_id
        :return: session
        """
        try:
            session = Session.nodes.get(session_id=session_id)
            return session
        except DoesNotExist:
            return Response(('{"No Content": "No session node found"}'), status = 200, mimetype = 'application/json')

def get_paginated_list(klass, url, start, limit):
    # check if page exists
    results = klass.query.all()
    count = len(results)
    if (count < start):
        pass
        # abort(404)
    # make response
    obj = {}
    obj['start'] = start
    obj['limit'] = limit
    obj['count'] = count
    # make URLs
    # make previous url
    if start == 1:
        obj['previous'] = ''
    else:
        start_copy = max(1, start - limit)
        limit_copy = start - 1
        obj['previous'] = url + '?start=%d&limit=%d' % (start_copy, limit_copy)
    # make next url
    if start + limit > count:
        obj['next'] = ''
    else:
        start_copy = start + limit
        obj['next'] = url + '?start=%d&limit=%d' % (start_copy, limit)
    # finally extract result according to bounds
    obj['results'] = results[(start - 1):(start - 1 + limit)]
    return obj
