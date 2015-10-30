
import datetime
import json


def to_time(numeric_string, as_date=False):
    """
    Converts UTC timestamp to string-formatted data time.

    :param int numeric_string: UTC timestamp
    """
    if as_date:
        date_format = '%Y-%m-%d'
    else:
        date_format = '%Y-%m-%d %H:%M:%S'
    time_as_date = datetime.datetime.utcfromtimestamp(int(numeric_string))
    return time_as_date.strftime(date_format)


def to_json(raw_data):
    """
    Pretty-prints JSON data

    :param str raw_data: raw JSON data
    """
    return json.dumps(raw_data, sort_keys=True,
                      indent=4, separators=(',', ': '))
