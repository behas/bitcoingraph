
import datetime
import json
import os
import subprocess
import sys


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


def sort(path, filename, args=''):
    if sys.platform == 'darwin':
        s = 'LC_ALL=C gsort -S 50% --parallel=4 {0} {1} -o {1}'
    else:
        s = 'LC_ALL=C sort -S 50% --parallel=4 {0} {1} -o {1}'
    status = subprocess.call(s.format(args, os.path.join(path, filename)), shell=True)
    if status != 0:
        raise Exception('unable to sort file: {}'.format(filename))
