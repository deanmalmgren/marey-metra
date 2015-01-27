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
