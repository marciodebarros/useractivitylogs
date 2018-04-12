import logging

#from flask_restplus import Resource, fields
from neomodel.core import DoesNotExist
from werkzeug.exceptions import BadRequest
from quart import Response


from app.api.restplus import api
from app.models import User

log = logging.getLogger(__name__)

ns = api.namespace('users', description='Users')

user = api.model('user', {
    'id': fields.Integer(readOnly=True, description='The internal id of of a user'),
    'user_id': fields.String(required=True, description='The user unique identifier')}
)

@ns.route('/')
@api.response(404, 'Users not found.')
class UsersList(Resource):

    @api.marshal_list_with(user)
    def get(self):
        """
        Returns a list of all users
        :return: list_of_users
        """
        try:
            users = User.nodes
            list_of_users = list(users)
            return list_of_users
    #        return json.dumps(dict(users = [user.serialize for user in list_of_users]))
        except DoesNotExist:
            return Response(('{"No Content": "No user nodes found"}'), status = 200, mimetype = 'application/json')


@ns.route('/<string:user_id>')
class UserItem(Resource):

   @api.marshal_with(user)
   def get(self, user_id):
        """
        Returns a user with the given user_id
        :param id: user_id
        :return: user
        """
        try:
            user_node = User.nodes.get(user_id=user_id)
            return user_node
        except DoesNotExist:
             raise DoesNotExist('Called from user route')






