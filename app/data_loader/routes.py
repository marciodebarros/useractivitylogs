import csv
import json
import os
import os.path
from datetime import datetime
from functools import singledispatch
import asyncio
from gremlin_python.structure.io import graphson


from goblin import Goblin
from app.config import Configuration
from app.utilities import prepare_event_date_time, is_db_connection_available
from app.data_loader.models import FileSummary, BatchSummary
from app.models import User, Environment, Session, Browser, Device, OS, BelongsTo, CompatibleWith, AssignedTo,\
    LogsIn, InstanceOf, ViewedOn, Exits, Accesses, Application, ApplicationInstance, Screen, ScreenInstance,\
    Tenant, Company, CloudSuite, Launches, Enters, LogsOut, TimesOut, ConnectedWith, Operates, Hosts, Provisioned,\
    Supports, RunsOn, Owns, Implemnts, DeployedFrom
from quart import Blueprint, Response
from more_itertools import peekable
from user_agents import parse




from functools import lru_cache


dataloader_mod = Blueprint('dataloader', __name__)

# Run the following command from the terminal every time the schema changes
# neomodel_install_labels app.py app.models --db 'bolt://neo4j:Password!@localhost:7687'




@singledispatch
def to_serializable(val):
    """Used by default."""
    return str(val)


@to_serializable.register(datetime)
def ts_datetime(val):
    """Used if *val* is an instance of datetime."""
    return val.isoformat() + "Z"


class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        # Java timestamp expects miliseconds
        ts = round(obj.timestamp() * 1000)
        return graphson.GraphSONUtil.typedValue('Date', ts)



loop = asyncio.get_event_loop()

def get_hashable_id(val):
    #Use the value "as-is" by default.
    result = val
    if isinstance(val, dict) and "@type" in val and "@value" in val:
        if val["@type"] == "janusgraph:RelationIdentifier":
            result = val["@value"]["value"]
    return result


#eader = graphson.GraphSONReader({'g:Date': DateDeserializer()})
#writer = graphson.GraphSONWriter({datetime.datetime: DateSerializer()})

#message_serializer = serializer.GraphSONMessageSerializer(reader=reader,
#                                                          writer=writer)


goblin_app = loop.run_until_complete(Goblin.open(loop,
    get_hashable_id=get_hashable_id))
#, message_serializer=message_serializer))


#goblin_app = loop.run_until_complete(Goblin.open(loop,
#                                                 hosts = ['localhost'],
#                                                 port = '8182',
#                                                 scheme = 'ws'))

#list_of_vertices = Goblin.vertices



goblin_app.register(User, Environment, Session, Browser, Device, OS, BelongsTo, CompatibleWith, AssignedTo, LogsIn,
                 InstanceOf, ViewedOn, Exits, Accesses, Application, ApplicationInstance, Screen, ScreenInstance,
                 Tenant, Company, CloudSuite, Launches, Enters, LogsOut, TimesOut, ConnectedWith, Operates, Hosts,
                 Provisioned, Supports, RunsOn, Owns, Implemnts, DeployedFrom
                 )


db_task = loop.create_task(goblin_app.session())


@dataloader_mod.route('/allfiles/')
async def load_all_files():
    "Loads all the files in the source directory"
    # if not (is_db_connection_available()):
    #    return Response(('{"Error": "Could not connect to the database"}'), status=404, mimetype='application/json')

    list_of_files = [f for f in os.listdir(Configuration.FILE_DIRECTORY)
                     if f.endswith(Configuration.INPUT_FILE_EXTENSION)]
    batch_stats = BatchSummary()

    if len(list_of_files) > 0:
        batch_stats.set_batch_start_date_time()
        for cur_file in list_of_files:
            file_stats = FileSummary()
            file_stats.set_file_name(cur_file)
            try:
                process_task = loop.create_task(process_file(cur_file, file_stats))
                file_stats = await process_task
                batch_stats.add_file(file_stats)
            finally:
                pass
                #loop.close()
        batch_stats.set_batch_end_date_time()
        return json.dumps(batch_stats.toJSON())
    else:
        return Response(('{"Error": "No files found on folder %s"}' % Configuration.FILE_DIRECTORY),
                        status=404, mimetype='application/json')


@dataloader_mod.route('/<file_name>')
async def load_one_file(file_name):

#    if not (is_db_connection_available()):
#        return Response(('{"Error": "Could not connect to the database"}'), status=404, mimetype='application/json')

    "Loads the file with the given name from the source directory"
    if os.path.exists(Configuration.FILE_DIRECTORY + file_name):
        file_stats = FileSummary()
        file_stats.set_file_name(file_name)
        file_stats = process_file(file_name, file_stats)
        return json.dumps(file_stats.toJSON())
    else:
        return Response(('{"Error": "File %s not found"}' % file_name), status=404, mimetype='application/json')



async def process_file(file_name, file_stats):

    db_session = await db_task
    "Loads the file in the source directory with the name passed as argument"
    rows = []
    with open(Configuration.FILE_DIRECTORY + file_name, 'r') as logfile:

        # Check if a previous reject file with the same name exists, and deletes it.
        if (os.path.exists(Configuration.FILE_DIRECTORY + file_name + '.' + Configuration.REJECTED_FILE_EXTENSION)):
            os.remove(Configuration.FILE_DIRECTORY + file_name + '.'  + Configuration.REJECTED_FILE_EXTENSION)

        os.rename(Configuration.FILE_DIRECTORY + file_name, Configuration.FILE_DIRECTORY + file_name + '.'
                  + Configuration.IN_PROGRESS_FILE_EXTENSION)
        logreader = csv.reader(logfile, delimiter=',')

        file_stats.set_file_start_date_time()


        for row in logreader:
            if (len(row) == 11):
                row += peekable(logreader).peek()
                if (len(row) == 15):
                    row[13] += row[14]
                    row = row[:-1]
            if ((len(row) == 13) or (len(row) == 14)):
                if not (len(row) == 13):
                    row[12] += row[13]
                task_process_rows = asyncio.ensure_future(process_rows(row, file_name, file_stats, db_session))
                file_stats = await task_process_rows
                if file_stats is None:
                    return file_stats
            else:
                rejected_file = open(Configuration.FILE_DIRECTORY + file_name + '.'
                                     + Configuration.REJECTED_FILE_EXTENSION, 'a+')
                rejected_file.write(str(row))
                file_stats.count_rejects()

        file_stats.set_file_end_date_time()

        os.rename(Configuration.FILE_DIRECTORY + file_name + '.' +  Configuration.IN_PROGRESS_FILE_EXTENSION,
              Configuration.FILE_DIRECTORY + file_name + '.' + Configuration.DONE_FILE_EXTENSION)
    return file_stats


async def process_rows(row, file_name, file_stats, db_session):
    message_types = ['Logged in', 'Launched', 'Entered' , 'Exited', 'Accessed', 'Logged out', 'Time out']
    application_required_messages = ['Launched', 'Entered' , 'Exited', 'Accessed']


    if ((row[0] in message_types) and (not row[0] in application_required_messages or str(row[8]).startswith('lid://'))):
        file_stats, db_session = process_function(message_types.index(row[0]), row, file_stats, db_session)
        await db_session.flush()

    else:
        rejected_file = open(Configuration.FILE_DIRECTORY + file_name + '.'
                             + Configuration.REJECTED_FILE_EXTENSION, 'a+')
        rejected_file.write(str(row))
        file_stats.count_rejects()
    return file_stats



def process_function(argument, row, file_stats, db_session):
    switcher = {
        0: process_log_in,
        1: process_launch_application,
        2: process_enter_application,
        3: process_exit_application,
        4: process_access_screen,
        5: process_log_out,
        6: process_time_out
    }
    # Get the function from switcher dictionary
    func = switcher.get(argument, lambda: "nothing")
    # Execute the function
    return func(row, file_stats, db_session)



def process_common_fields(row, db_session):

    created_nodes = {'event_date_time': None, 'session':None, 'user':None, 'tenant':None, 'environment':None,
                     'company':None, 'cloud_suite': None, 'application':None, 'application_instance':None,
                     'screen':None, 'screen_instance':None, 'os':None, 'browser':None, 'device':None
                        }

    event_date_time = prepare_event_date_time(row[3])

    created_nodes['event_date_time'] = json.dumps(event_date_time, default=to_serializable)

    user_agent_str = row[12]
    if len(row) > 13:
        user_agent_str += row[13]

    user = get_user_node(row[4])

    # Check if the call to get a user returns None, something went wrong, most likely the could not
    # connect to the database, so we need to abort.
    if user is None:
        file_stats = None
        return file_stats

    created_nodes['user'] = user
    db_session.add(user)

    session = get_session_node(row[10])
    session = set_session_properties(session, row[6], None, None, None)

    created_nodes['session'] = session
    db_session.add(session)

    assigned_to = AssignedTo(session, user)
    db_session.add(assigned_to)

    tenant_id = row[5]
    if row[2] == 'OP':
        tenant_id = row[7][:row[7].index('.')] + '_' + row[5]

    tenant = get_tenant_node(tenant_id)
    created_nodes['tenant'] = tenant
    db_session.add(tenant)

    if row[11]:
        if row[11] == row[5]:
            company_name = row[11][:row[11].index('_')]
        else:
            company_name = row[11]

        company = get_company_node(company_name)

        if company is not None:
            created_nodes['company'] = company
            db_session.add(company)

            owns = Owns()
            owns.source = company
            owns.target = tenant
            db_session.add(owns)

    environment = get_environment_node(row[7], row[2])
    created_nodes['enviornment'] = environment
    db_session.add(environment)

    hosts = Hosts()
    hosts.source = environment
    hosts.target = tenant
    db_session.add(hosts)

    browser = get_browser_node(user_agent_str)
    created_nodes['browser'] = browser
    db_session.add(browser)

    device = get_device_node(user_agent_str)
    created_nodes['device'] = device
    db_session.add(device)

    os = get_os_node(user_agent_str)
    created_nodes['os'] = os
    db_session.add(os)

    runs_on = RunsOn()
    runs_on.source = browser
    runs_on.target = device
    db_session.add(runs_on)

    supports = Supports()
    supports.source = browser
    supports.target = os
    db_session.add(supports)

    operates = Operates()
    operates.source = os
    operates.target = device
    db_session.add(operates)

    connected_with = ConnectedWith()
    connected_with.source = session
    connected_with.target = browser
    db_session.add(connected_with)

    return created_nodes, db_session

async def create_aplication_and_instance_nodes(row, created_nodes, db_session):

    application_instance = get_application_instance_node(row[8])
    created_nodes['application_instance'] = application_instance
    db_session.add(application_instance)

    application = get_application_node(parse_application_name(row[8]))
    created_nodes['application'] = application
    db_session.add(application)

    compatible_with = CompatibleWith()
    compatible_with.source = application
    compatible_with.target = created_nodes['browser']
    db_session.add(compatible_with)

    deployed_from = DeployedFrom()
    deployed_from.source = application_instance
    deployed_from.target = application
    db_session.add(deployed_from)

    if row[1]:
        cloud_suite = get_cloud_suite_node(row[1])
        created_nodes['cloud_suite'] = cloud_suite
        db_session.add(cloud_suite)

        belongs_to = BelongsTo()
        belongs_to.source = application
        belongs_to.target = cloud_suite
        db_session.add(belongs_to)

    return created_nodes, db_session



def process_log_in(row, file_stats, db_session):

    created_nodes, db_session = process_common_fields(row, db_session)

    session = created_nodes['session']
    tenant = created_nodes['tenant']
    login_date_time = created_nodes['event_date_time']
    session = set_session_properties(session, None, login_date_time, None, None)

    log_in = LogsIn()
    log_in.source = session
    log_in.target = tenant
    log_in.action_timestamp = login_date_time

    db_session.add(log_in)

    file_stats.count_logged_in()

# TODO -- Ensure that all objects (Vertices and Edges) are added to the db_session, and that they are not added twice

    return file_stats, db_session


async def process_launch_application(row, file_stats, db_session):

    created_nodes, db_session = process_common_fields(row, db_session)
    session = created_nodes['session']

    tenant = created_nodes['tenant']

    launch_date_time = created_nodes['event_date_time']

    created_nodes, db_session = create_aplication_and_instance_nodes(row, created_nodes, db_session)

    application_instance = created_nodes['application_instance']
    application = created_nodes['application']

    provisioned = Provisioned()
    provisioned.source = tenant
    provisioned.target = application
    db_session.add(provisioned)

    launches = Launches()
    launches.action_timestamp = launch_date_time
    launches.source = session
    launches.target = application_instance
    db_session.add(launches)

    file_stats.count_lauched()

    return file_stats, db_session

async def process_enter_application(row, file_stats):

    created_nodes, db_session = process_common_fields(row, db_session)

    session = created_nodes['session']
    tenant = created_nodes['tenant']
    enter_date_time = created_nodes['event_date_time']

    created_nodes = create_aplication_and_instance_nodes(row, created_nodes)

    application_instance = created_nodes['application_instance']
    application = created_nodes['application']

    provisioned = Provisioned()
    provisioned.source = tenant
    provisioned.target = application
    db_session.add(provisioned)

    enters = Enters()
    enters.action_timestamp = enter_date_time
    enters.source = session
    enters.target = application_instance
    db_session.add(enters)

    file_stats.count_entered()

    return file_stats


async def process_access_screen(row, file_stats, db_session):

    created_nodes = process_common_fields(row, db_session)
    session = created_nodes['session']
    tenant = created_nodes['tenant']
    access_date_time = created_nodes['event_date_time']

    created_nodes = create_aplication_and_instance_nodes(row, created_nodes)
    application = created_nodes['application']
    application_instance = created_nodes['application_instance']

    provisioned = Provisioned()
    provisioned.source = tenant
    provisioned.target = application
    db_session.add(provisioned)

    screen_name = row[9]
    if row[9]: #Check if there is a string with the screen name
        if not row[9].startswith(get_application_name(row[8])):
            screen_name = get_application_name(row[8]) + '_' + row[9]
    else:
        screen_name = get_application_name(row[8]) + '_' + 'Unknown'

    screen_instance = get_screen_instance_node(screen_name)
    db_session.add(screen_instance)

    screen = get_screen_node(screen_name)
    db_session.add(screen)

    instance_of = InstanceOf()
    instance_of.source = screen_instance
    instance_of.target = screen
    db_session.add(instance_of)

    viewed_on = ViewedOn()
    viewed_on.source = screen_instance
    viewed_on.target = application_instance
    db_session.add(viewed_on)

    accesses = Accesses()
    accesses.action_timestamp = access_date_time
    accesses.source = session
    accesses.target = screen_instance
    db_session.add(accesses)

    implements = Implemnts()
    implements.source = application
    implements.target = screen
    db_session.add(implements)

    file_stats.count_accessed()

    return file_stats


async def process_exit_application(row, file_stats, db_session):
    created_nodes = process_common_fields(row, db_session)
    session = created_nodes['session']
    tenant = created_nodes['tenant']
    exit_date_time = created_nodes['event_date_time']

    created_nodes = create_aplication_and_instance_nodes(row, created_nodes)
    application = created_nodes['application']
    application_instance = created_nodes['application_instance']

    exits = Exits()
    exits.action_timestamp = exit_date_time
    exits.source = session
    exits.target = application_instance
    db_session.add(exits)

    provisioned = Provisioned()
    provisioned.source = tenant
    provisioned.target = application
    db_session.add(provisioned)


    file_stats.count_exited()

    return file_stats


async def process_log_out(row, file_stats, db_session):
    created_nodes = process_common_fields(row, db_session)
    session = created_nodes['session']
    tenant = created_nodes['tenant']
    logout_date_time = created_nodes['event_date_time']

    set_session_properties(session, None, None, logout_date_time, None)

    log_out = LogsOut()
    log_out.action_timestamp = logout_date_time
    log_out.source = session
    log_out.target = tenant
    db_session.add(log_out)

    file_stats.count_logged_out()

    return file_stats


async def process_time_out(row, file_stats, db_session):

    created_nodes = process_common_fields(row, db_session)
    session = created_nodes['session']
    tenant = created_nodes['tenant']
    timeout_date_time = created_nodes['event_date_time']

    set_session_properties(session, None, None, None, timeout_date_time)

    time_out = TimesOut()
    time_out.action_timestamp = timeout_date_time
    time_out.source = session
    time_out.target = tenant
    db_session.add(time_out)

    file_stats.count_timed_out()

    return file_stats


def get_device_type(user_agent):
    device_type = ''
    if user_agent.is_pc:
        device_type = 'DLT'
    elif user_agent.is_mobile:
        device_type = 'MOB'
    elif user_agent.is_tablet:
        device_type = 'TAB'
    elif user_agent.is_bot:
        device_type = 'BOT'
    else:
        device_type = 'UNK'
    return device_type



def get_session_node(session_id):
    session = None
    if session_id is not None:
        session = Session()
        session.session_id = session_id
    return session


def set_session_properties(session, ip_address, session_start, session_end, session_timeout):
    if ip_address is not None:
        if session.ip_address is None:
            session.ip_address = set()
            session.ip_address.add(str(ip_address))
        #if (str(ip_address) not in session.ip_address):
            #session.ip_address = (str(ip_address))
        #    session.ip_address.add(str(ip_address))
        if session_start is not None and session.start is None:
            session.start = session_start
        if session_end is not None and session.end is None:
            session.end = session_end
        if session_timeout is not None and session.time_out is None:
            session.time_out = session_timeout
    return session

def get_user_node(user_id):
    user = None
    if user_id is not None:
        user = User()
        user.user_id = user_id
    return user


def get_application_node(application_name):
    application = None
    if application_name is not None:
        application = Application()
        application.name = application_name
    return application

def get_application_instance_node(application_id):
    application_instance = None
    if application_id is not None:
        application_instance = ApplicationInstance()
        application_instance.application_id = application_id
    return application_instance


def get_screen_node(screen_name):
    screen = None
    if screen_name is not None:
        screen = Screen()
        screen.name = screen_name
    return screen


def get_screen_instance_node(screen_id):
    screen_instance = None
    if screen_id is not None:
        screen_instance = ScreenInstance()
        screen_instance.screen_id = screen_id
    return screen_instance


def get_environment_node(server_id, environment_type):
    environment = None
    if server_id is not None and environment_type is not None:
        environment = Environment()
        environment.server = server_id
        environment.type = environment_type
    return environment


def get_tenant_node(tenant_id):
    tenant = None
    if (tenant_id is not None):
        tenant = Tenant()
        tenant.tenant_id = tenant_id
    return tenant

def get_cloud_suite_node(cloud_suite_name):
    cloud_suite = None
    if (cloud_suite_name is not None):
        cloud_suite = CloudSuite()
        cloud_suite.name = cloud_suite_name
    return cloud_suite

def get_browser_node(user_agent_str):
    if user_agent_str is not None:
        user_agent = parse(user_agent_str)
        browser = Browser()
        browser.type = user_agent.browser.family
        browser.version = user_agent.browser.version_string
    return browser


def get_device_node(user_agent_str):
    if user_agent_str is not None:
        user_agent = parse(user_agent_str)

        if user_agent.device.brand is not None:
            device_brand = user_agent.device.brand
        else:
            device_brand = 'Unknown'

        if user_agent.device.model is not None:
            device_model = user_agent.device.model
        else:
            device_model = 'Unknwon'

        touch_capable = 'N'
        if user_agent.is_touch_capable:
            touch_capable = 'Y'

        device_type = ''
        if user_agent.is_pc:
            device_type = 'DLT'
        elif user_agent.is_mobile:
            device_type = 'MOB'
        elif user_agent.is_tablet:
            device_type = 'TAB'
        elif user_agent.is_bot:
            device_type = 'BOT'
        else:
            device_type = 'UNK'

        device = Device()
        device.family = user_agent.device.family
        device.brand = device_brand
        device.model = device_model
        device.type = device_type
        device.is_touch_capable = touch_capable

    return device

def get_company_node(company_name):
    if company_name is not None:
        company = Company()
        company.name = company_name
    return company

def get_os_node(user_agent_str):
    "Return a OS Vertex"
    if user_agent_str is not None:
        user_agent = parse(user_agent_str)
        os = OS()
        os.family = user_agent.os.family
        os.version = user_agent.os.version_string
    return os

async def reject_record(file_name, row, file_stats):
    rejected_file = open(Configuration.FILE_DIRECTORY + file_name + '.'
                         + Configuration.REJECTED_FILE_EXTENSION, 'a+')
    rejected_file.write(str(row))
    return file_stats.count_rejects()


async def parse_application_name(application_id):
    application_name = application_id[:application_id.rfind('.')]
    return application_name

async def get_application_name(application_id):
    application_name = application_id[(application_id.find('.')+1):application_id.rfind('.')]
    return application_name