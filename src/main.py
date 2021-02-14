#!/usr/bin/python

import sys
import os
import yaml
from Init import Init


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
    Init(yml_settings)


if __name__ == '__main__':
    if len(sys.argv) == 2:
        main(sys.argv[1])
    else:
        print('Error: Please pass the path to the settings file as argument')

