#!/usr/bin/python

import sys
import os
import yaml
import click
import logging
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

    now = datetime.now()

    logging.basicConfig(format='[%(asctime)s] %(levelname)-8s %(name)-10s %(message)s', filename='backup.log', level=logging.INFO)
    logger = logging.getLogger('main')

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

    logger.info('==============================================')
    logger.debug('Backup invoked with the following options:')
    logger.info('  Configuration file: {}'.format(config))
    logger.debug('  Don''t use relative paths: {}'.format(no_relatives))
    if ssh:
        logger.debug('  ssh: {}'.format(ssh))
        logger.debug('  host: {}'.format(host))
        logger.debug('  user: {}'.format(user))
        logger.debug('  port: {}'.format(port))

    # Check for doubled entries in the prio field
    prios = []
    for i in yml_config['intervals']:
        prios.append(i['prio'])
    if len(prios) != len(set(prios)):
        logger.error('Double defined priorities in {} found'.format(config))
        raise ValueError
    # Setup base folders and if needed create a new full backup
    init = Init(now, yml_config)
    backup = Backup(yml_config, init.get_backup_target(),  now)

    end = datetime.now()
    seconds = (end - now).total_seconds()
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    logger.info('Execution time: {} hrs {} mins {} secs'.format(hours, minutes, seconds))


if __name__ == '__main__':
    main()

