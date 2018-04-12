from flask import Blueprint, Response, jsonify, Flask, abort, request
from app.models import User, Tenant, Application, Session, Screen, Browser, OS, Device, Environment
from neomodel.core import DoesNotExist
from flask_restplus import Api, Resource, fields
import json
from app import api


api_mod = Blueprint('api', __name__, url_prefix='/api/1')




@api_mod.route('/tenants')
def get_tenants():
    try:
        tenants = Tenant.nodes
        list_of_tenants = list(tenants)
        return json.dumps(dict(tenants = [tenant.serialize for tenant in list_of_tenants]))
    except Tenant.DoesNotExist:
        return Response(('{"No Content": "No tenant nodes found"}'), status = 200, mimetype='application/json')


@api_mod.route('/applications')
def get_applications():
    try:
        applications = Application.nodes
        list_of_applications = list(applications)
        return json.dumps(dict(applications = [application.serialize for application in list_of_applications]))
    except DoesNotExist:
        return Response(('{"No Content": "No application nodes found}'), status = 200, mimetype='application/json')

@api_mod.route('/sessions')
def get_sessions():
    try:
        sessions = Session.nodes
        list_of_sessions = list(sessions)
        return json.dumps(dict(sessions = [session.serialize for session in list_of_sessions]))
    except DoesNotExist:
        return Response(('{"No Content": "No session nodes found"}'), status = 200, mimetype='application/json')


@api_mod.route('/browsers')
def get_browsers():
    try:
        browsers = Browser.nodes
        list__of_browsers = list(browsers)
        return json.dumps(dict(browsers = [browser.serialize for browser in list__of_browsers]))
    except DoesNotExist:
        return Response(('{"No Content": "No browser nodes found"}'), status = 200, mimetype='application/json')


@api_mod.route('/os')
def get_os():
    try:
        oss = OS.nodes
        list_of_os = list(oss)
        return json.dumps(dict(os = [os.serialize for os in list_of_os]))
    except DoesNotExist:
        return Response(('{"No Content": "No OS nodes found"}'), status = 200, mimetype='application/json')


@api_mod.route('/devices')
def get_devices():
    try:
        devices = Device.nodes
        list_of_devices = list(devices)
        return json.dumps(dict(devices = [device.serialize for device in list_of_devices]))
    except DoesNotExist:
        return Response(('{"No Content": "No device nodes found"}'), status = 200, mimetype='application/json')

@api_mod.route('/environments')
def get_enviornments():
    try:
        environments = Environment.nodes
        list_of_environments = list(environments)
        return json.dumps(dict(environments = [environment.serialize for environment in list_of_environments]))
    except DoesNotExist:
        return Response(('{"No Content": "No enviroment nodes found"}'), status = 200, mimetype='application/json')

@api_mod.route('/pagesessions')
def get_session_page():
    try:
        sessions = Session.nodes
        list_of_sessions = list(sessions)
        return jsonify(get_paginated_list(dict(sessions = [session.serialize for session in list_of_sessions]), '/api/pagesessions',
                                          start=request.args.get('start', 1),
                                          limit=request.args.get('limit', 20)
                                          ))
    except DoesNotExist:
        return Response(('{"No Content": "No session page nodes found"}'), status=200, mimetype='application/json')



def get_paginated_list(klass, url, start, limit):
    # check if page exists
    results = klass
    count = len(results)
    if (count < start):
        abort(404)
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