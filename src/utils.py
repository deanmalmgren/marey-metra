import re
import datetime


def strip(row):
    """strip all extra space off of native python objects"""
    if isinstance(row, dict):
        return dict((k.strip(), v.strip()) for k, v in row.iteritems())
    elif isinstance(row, list):
        return [x.strip() for x in row]
    else:
        raise TypeError

def js2pydate(js_string):
    """Convert the gross '/Date(#########)/' format to a datetime"""
    timestamp = re.match(
        '/Date\((?P<timestamp>[0-9]+)\)/',
        js_string,
    ).groupdict()['timestamp']
    return datetime.datetime.fromtimestamp(int(timestamp)/1000)
