import logging

from flask import Response
from flask_restplus import Resource, fields
from neomodel.core import DoesNotExist
from neomodel import MultipleNodesReturned


from app.api.restplus import api
from app.models import Browser

log = logging.getLogger(__name__)

ns = api.namespace('browsers', description='Browsers')

browser = api.model('browser', {
    'id': fields.Integer(readOnly=True, description='The internal id of the browser.'),
    'type': fields.String(required=True, description='The type of the browser.'),
    'version': fields.String(required=True, description='The version of the browser.')
})

@ns.route('/')
class BrowserList(Resource):

    @api.marshal_list_with(browser)
    def get(self):
        """
        Returns a list with all browsers
        :return: list_of_browsers
        """
        try:
            browsers = Browser.nodes
            list__of_browsers = list(browsers)
            return list__of_browsers
        except DoesNotExist:
            return Response(('{"No Content": "No browser nodes found"}'), status=200, mimetype='application/json')

@ns.route('/<string:browser_type>')
class BrowserItem(Resource):

    @api.marshal_list_with(browser)
    def get(self, browser_type):
        """
        Return a browser with the given type
        :param browser_type:
        :return: browser
        """
        try:
            browser = Browser.nodes.get(type=browser_type)
            return browser
        except DoesNotExist:
            raise DoesNotExist ('Browser not found')
        except MultipleNodesReturned:
            raise MultipleNodesReturned('Multiple entries for browser type')




@ns.route('/<string:browser_type>/versions/')
class BrowserVersions(Resource):

    @api.marshal_list_with(browser)
    def get(self, browser_type):
        """
        Return all the versions available for a given browser
        :param browser_type:
        :return: list of browsers
        """
        try:

            # Cypher gets us the Assets we want
            query = "MATCH (n:Browser {type:{browser_type}}) RETURN n ORDER BY n.version ASC"
            results, meta = db.cypher_query(query, {'browser_type': browser_type})

            browser = [Browser.inflate(row[0]) for row in results]
            return browser

        except DoesNotExist:
            raise DoesNotExist("Browser not found")


