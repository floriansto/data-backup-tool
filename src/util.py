#!/usr/bin/python

from datetime import datetime
from datetime import timedelta
import os
import shutil


def cleanup(path):
    """
    Cleanup after e.g. a crash or SIGINT
    :param path: Path to check (Symlink path to last (failed) backup)
    """
    if path is not None and os.path.exists(path):
        shutil.rmtree(os.path.realpath(path))
        os.remove(path)


def t_delta_from_config(cycle):
    """
    Create a datetime.timedelta object from a dict
    :param cycle: Dict containing offsets
    :return: datetime.timedelta object
    """
    return timedelta(days=cycle['days'], hours=cycle['hours'],
                     minutes=cycle['minutes'], seconds=cycle['seconds'])


def time_from_str(src, date_format):
    """
    Create a datetime object from a time string and a given format
    :param src: time string
    :param date_format: defines how to interpret the time string
    :return: datetime.datetime object
    """
    return datetime.strptime(src, date_format)
