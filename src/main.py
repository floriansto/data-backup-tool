#!/usr/bin/python

import sys
import os
import yaml
from datetime import datetime
from Init import Init
from Backup import Backup


def main(settings):
    # Parse configuration yaml file
    if settings is None or not os.path.isfile(settings):
        print('Error: invalid settings file: {}'.format(settings))
        raise ValueError
    with open(settings) as f:
        yml_settings = yaml.safe_load(f)

    # Check for doubled entries in the prio field
    prios = []
    for i in yml_settings['backup']['intervals']:
        prios.append(i['prio'])
    if len(prios) != len(set(prios)):
        print('Double defined priorities in {} found'.format(settings))
        raise ValueError
    # Setup base folders and if needed create a new full backup
    now = datetime.now()
    init = Init(now, yml_settings)
    backup = Backup(yml_settings, init.get_backup_target(),  now)


if __name__ == '__main__':
    if len(sys.argv) == 2:
        main(sys.argv[1])
    else:
        print('Error: Please pass the path to the settings file as argument')

