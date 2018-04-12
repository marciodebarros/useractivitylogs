from neo4j.exceptions import ServiceUnavailable
from neomodel import db
from datetime import datetime
from app.config import Configuration
import os
import time

def is_db_connection_available():
    query = 'MATCH (n) RETURN count(n);'
    is_available = False
    try:
        results = db.cypher_query(query)
        is_available = True
    except ServiceUnavailable:
        pass
    return is_available

def myconverter(o):
    "Converts a date/time object to a string"
    if isinstance(o, datetime):
        return o.__str__()

def prepare_event_date_time(row_date_time):
    try:
        event_start_datetime_datetime = datetime.strptime(row_date_time.replace('.',':'),"%Y-%m-%d %H:%M:%S")
        event_start_datetime = event_start_datetime_datetime.timestamp()

    except ValueError:
        event_start_datetime = None
    return event_start_datetime


def prepare_rerun():
    list_of_files = [f for f in os.listdir(Configuration.FILE_DIRECTORY)
                     if f.endswith(Configuration.DONE_FILE_EXTENSION)]
    if len(list_of_files) > 0:
        for file_name in list_of_files:
            file_name.replace(Configuration.DONE_FILE_EXTENSION, '')
            # os.rename(Configuration.FILE_DIRECTORY + file_name,
            #           Configuration.FILE_DIRECTORY + file_name + '.'
                      # + Configuration.INPUT_FILE_EXTENSION)


