import json
from goblin import Goblin, element, properties
from gremlin_python.process.traversal import Cardinality
from app.custom import goblin_data_types


from app.utilities import myconverter

#config.DATABASE_URL = 'bolt://neo4j:Password!@localhost:7687'


class LogsIn(element.Edge):
    action_timestamp =  properties.Property(properties.Float) ## Logged in action

class Launches(element.Edge):
    action_timestamp = properties.Property(properties.Float) ## Launch and applicaiton in action

class Accesses(element.Edge):
    action_timestamp = properties.Property(properties.Float) ## Accessed in action

class Enters(element.Edge):
    action_timestamp = properties.Property(properties.Float) ## Entered in action

class Exits(element.Edge):
    action_timestamp = properties.Property(properties.Float) ##Exited action

class LogsOut(element.Edge):
    action_timestamp = properties.Property(properties.Float) ## Logged out action

class TimesOut(element.Edge):
    action_timestamp = properties.Property(properties.Float) ## Time out action

class AssignedTo(element.Edge):
    pass

class ConnectedWith(element.Edge):
    pass

class Operates(element.Edge):
    pass

class Hosts(element.Edge):
    pass

class Provisioned(element.Edge):
    pass

class Supports(element.Edge):
    pass

class RunsOn(element.Edge):
    pass

class Owns(element.Edge):
    pass

class BelongsTo(element.Edge):
    pass

class DeployedFrom(element.Edge):
    pass

class Implemnts(element.Edge):
    pass

class InstanceOf(element.Edge):
    pass

class ViewedOn(element.Edge):
    pass

class CompatibleWith(element.Edge):
    pass



class Browser(element.Vertex):
    type = properties.Property(properties.String)
    version = properties.Property(properties.String)

    @property
    def serialize(self):
        return {
            'type': self.type,
            'version': self.version
        }


class OS(element.Vertex):
    family = properties.Property(properties.String)
    version = properties.Property(properties.String)
#    operates = Relationship('Device', 'OPERATES')

    @property
    def serialize(self):
        return {
            'family': self.family,
            'version': self.version
        }


class Device(element.Vertex):

    DEVICE_TYPES = (
        ('MOB', 'Mobile'),
        ('TAB', 'Tablet'),
        ('BOT', 'Bot, Spider or Crawler'),
        ('DLT', 'Desktop or Laptop'),
        ('UNK', 'Unknwonn')
    )

    TOUCH_CAPABLE = (
        ('Y', 'Touch Capable'),
        ('N', 'No Touch Capable ')

    )

    family = properties.Property(properties.String)
    brand = properties.Property(properties.String)
    model = properties.Property(properties.String)
    type = properties.Property(properties.String)
    is_touch_capable = properties.Property(properties.Boolean)

    #type = properties.Property(required=True, choices=DEVICE_TYPES)
    #is_touch_capable = properties.Property(required=True, choices=TOUCH_CAPABLE)

    @property
    def serialize(self):
        return {
            'family': self.family,
            'brand': self.brand,
            'model': self.model,
            'type': self.type,
            'is_touch_capable': self.is_touch_capable
        }



class Environment(element.Vertex):

    ENVIRONMENT_TYPES = (
        ('OP', 'On-premises'),
        ('ST', 'Single Tenant'),
        ('MT', 'Multi Tenant'),
        ('DEMO', 'Demo/GDE')
    )
    server = properties.Property(properties.String)
    type = properties.Property(properties.String)
    #hosts = Relationship('Tenant', 'HOSTS')

    @property
    def serialize(self):
        return {
            'server': self.server,
            'type': self.type
        }

   #def get_all_tenants(self):
   #     query = 'MATCH (e:Environment)-[HOSTS]->(t:Tenant) WHERE e.server={server} return t'
   #     results, columns = self.cypher(query, {'server': self.server})
   #     return results


class Tenant(element.Vertex):
    tenant_id = properties.Property(properties.String)
    #provisioned = Relationship('Application', 'PROVISIONED')

    @property
    def serialize(self):
        return {
            'tenant_id': self.tenant_id
        }

#    def get_envirnment(self):
#        query = 'MATCH (t:Tenant)<-[HOSTS]-(e:Environment) WHERE t.tenant_id={tenant_id} return e'
#        results, columns = self.cypher(query, {'tenant_id': self.tenant_id})
#        return results

class User(element.Vertex):
    user_id = properties.Property(properties.String)

    @property
    def serialize(self):
        return {
            'user_id': self.user_id,
        }


class Session(element.Vertex):
    session_id = properties.Property(properties.String)
    ip_address = element.VertexProperty(properties.String, card=Cardinality.set_)
    start = properties.Property(properties.Float)
    end = properties.Property(properties.Float)
    timeout = properties.Property(properties.Float)

    #assigned_to = Relationship('User', 'ASSIGNED_TO')
    #log_in = Relationship('Tenant', 'LOG_IN', model=LogsIn)
    #log_out = Relationship('Tenant', 'LOGGED_OUT', model=LogsOut)
    #time_out = Relationship('Tenant', 'TIME_OUT', model=TimesOut)
    #launches = Relationship('ApplicationInstance', 'LAUNCHES', model=Launches)
    #enters = Relationship('ApplicationInstance', 'ENTERS', model=Enters)
    #exits = Relationship('ApplicationInstance', 'EXITS', model=Exits)
    #accesses = Relationship('ScreenInstance', 'ACCESSES', model=Accesses)
    #connected_with = Relationship('Browser', 'CONNECTED_WITH')

    def end_session_at(self, end_datetime):
        self.end = end_datetime
        self.save()

    def timeout_at(self, timeout_datetime):
        self.timeout = timeout_datetime
        self.save()

    @property
    def serialize(self):
        return {
            '_id': self.id,
            'session_id': self.session_id,
            'ip_addresses': json.dumps(self.ip_address).replace("u\'","\'"),
            'start': myconverter(self.start),
            'end': myconverter(self.end),
            'timeout': myconverter(self.timeout_at)
        }


class Application(element.Vertex):
    name = properties.Property(properties.String)
#    implements = Relationship('Screen', 'IMPLEMENTS')
#    belongs_to = Relationship('CloudSuite', 'BELONGS_TO')
#    compatible_with = Relationship('Browser', 'COMPATIBLE_WITH')
    @property
    def serialize(self):
        return {
 #           'id': self.id,
            'name': self.name
        }

    def get_all_screens(self):
        query = 'MATCH (a:Application)-[IMPLEMENTS]-(s:Screen) WHERE a.name={name} return s'
        results, columns = self.cypher(query, {'name': self.name})
        return results



class ApplicationInstance(element.Vertex):
    application_id = properties.Property(properties.String)
#    deployed_from =  Relationship('Application', 'DEPLOYED_FROM')

    @property
    def serialize(self):
        return {
    #        'id': self.id,
            'application_id': self.application_id
        }

    def get_all_screens(self):
        query = 'MATCH (a:ApplicationInstance)-[VIEWED_ON]-(s:ScreenInstance) WHERE a.application_id={application_id} return s'
        results, columns = self.cypher(query, {'application_id': self.application_id})
        return results


class Screen(element.Vertex):
    # -- TODO - Prefix all the screens with the application id portion of the LID.
    name = properties.Property(properties.String)
    @property
    def serialize(self):
        return {
        #    'id': self.id,
            'name': self.name
        }

class ScreenInstance(element.Vertex):
    screen_id = properties.Property(properties.String)
#    viewed_on = Relationship('ApplicationInstance', 'VIEWED_ON')
#    instance_of = Relationship('Screen', 'INSTANCE_OF')
    @property
    def serialize(self):
        return {
        #   'id': self.id,
            'screen_id': self.screen_id
        }



class Company(element.Vertex):
    name = properties.Property(properties.String)
#    owns = Relationship('Tenant', 'OWNS')
    @property
    def serialize(self):
        return {
         #   'id': self.id,
            'name': self.name
        }


class CloudSuite(element.Vertex):
    name = properties.Property(properties.String)
    @property
    def serialize(self):
        return {
         #   'id': self.id,
            'name': self.name
        }