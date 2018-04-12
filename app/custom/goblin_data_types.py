import datetime
import goblin
import json
from gremlin_python.structure.io import graphson



class DateSerializer:

    def dictify(self, obj, writer):
        # Java timestamp expects miliseconds
        ts = round(obj.timestamp() * 1000)
        return graphson.GraphSONUtil.typedValue('Date', ts)


class DateDeserializer:
    def objectify(self, ts, reader):
        # Python timestamp expects seconds
        dt = datetime.datetime.fromtimestamp(ts / 1000.0)
        return dt


class DateTime(goblin.abc.DataType):

    def validate(self, val):
        if not isinstance(val, datetime.datetime):
            raise goblin.exception.ValidationError(
                "Not a valid datetime.datetime: {}".format(val))
        return val

    # Note that these methods are different than in the previous example.
    def to_ogm(self, val):
        return super().to_ogm(val)

    def to_db(self, val):
        return super().to_db(val)

