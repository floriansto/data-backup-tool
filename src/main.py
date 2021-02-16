#!/usr/bin/python

import sys
import os
import yaml
import click
from datetime import datetime
from Init import Init
from Backup import Backup


@click.command()
@click.option('-s', '--ssh', is_flag=True, default=False, help='Use ssh connection to get backup files')
@click.option('-h', '--host', default='127.0.0.1', type=str, help='When using ssh, connect to this host. May be hostname or ip adress')
@click.option('-p', '--port', default=22, type=int, help='When using ssh, use this port')
@click.option('-u', '--user', default='root', type=str, help='When using ssh, use this user')
@click.option('-n', '--no-relatives', is_flag=True, default=False, help='Do not use relative path names. Disables the -R option of rsync.')
@click.argument('config', type=str)
def main(config, host, port, user, ssh, no_relatives):
    # Parse configuration yaml file
    if config is None or not os.path.isfile(config):
        print('Error: invalid config file: {}'.format(config))
        raise ValueError
    with open(config) as f:
        yml_config = yaml.safe_load(f)

    yml_config['user'] = user
    yml_config['port'] = port
    yml_config['host'] = host
    yml_config['no_rels'] = no_relatives
    yml_config['ssh'] = ssh

    # Check for doubled entries in the prio field
    prios = []
    for i in yml_config['backup']['intervals']:
        prios.append(i['prio'])
    if len(prios) != len(set(prios)):
        print('Double defined priorities in {} found'.format(config))
        raise ValueError
    # Setup base folders and if needed create a new full backup
    now = datetime.now()
    init = Init(now, yml_config)
    backup = Backup(yml_config, init.get_backup_target(),  now)


if __name__ == '__main__':
    main()

