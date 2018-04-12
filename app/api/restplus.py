from flask_restplus import Api, fields
from neomodel import MultipleNodesReturned
from neomodel.core import DoesNotExist


# 200 OK – the API request succeeded (general purpose)
# 201 Created – request to create a new record succeeded
# 204 No Content – the API request succeeded, but there is no response payload to return
# 400 Bad Request – the API request is bad or malformed and could not be processed by the server
# 404 Not Found – couldn’t find a record by ID


api = Api(version='1.0', title='Users Activity Log',
          description='An API to retreive information about users'' activities in Infor Ming.le')




base_reponse = api.model('meta', {'limit': fields.Integer})


@api.errorhandler(DoesNotExist)
def handle_node_does_not_exist_exception(error):
    return {'message': 'The {0} node {0} does not exist'}, 405


@api.errorhandler(MultipleNodesReturned)
def multiple_nodes_found_handler(error):
    return {'message': 'My error'}, 503


@api.errorhandler
def default_error_handler(error):
    return {'message': 'This is the default error'}, 503


        #
#class Error(Exception):
#    """Base class for exceptions in this module."""
#    pass

#class InputError(Error):
#    """Exception raised for errors in the input.

#    Attributes:
#        expression -- input expression in which the error occurred
#        message -- explanation of the error
#    """

#    def __init__(self, expression, message):
#        self.expression = expression
#        self.message = message
#        """