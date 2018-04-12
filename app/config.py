class Configuration(object):
    DEBUG = True
    FILE_DIRECTORY = '/Users/mdebarros/PycharmProjects/useractivitylogs/app/static/data/'
    DB_TYPE = 'JANUSGRAPH'
    JANUSGRAPH_DB_SERVER = 'localhost'
    JANUSGRAPH_DB_PORT = '8182'
    JANUSGRAPH_DB_SCHEMA = 'useractivitylogs'
    NEO4J_DB_PROTOCOL = 'bolt'
    NEO4J_DB_SERVER = 'localhost'
    NEO4J_DB_PORT = '7687'
    NEO4J_DB_USER = 'neo4j'
    NEO4J_DB_PASSWORD = 'Password!'
    NEO4J_DB_CLEAN_AT_START = False
    INPUT_FILE_EXTENSION = 'log.0'
    IN_PROGRESS_FILE_EXTENSION = 'ipg'
    DONE_FILE_EXTENSION = 'done'
    REJECTED_FILE_EXTENSION = 'rejected'
    FILE_RERUN = True

