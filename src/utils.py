def strip(row):
    if isinstance(row, dict):
        return dict((k.strip(), v.strip()) for k, v in row.iteritems())
    elif isinstance(row, list):
        return [x.strip() for x in row]
    else:
        raise TypeError
