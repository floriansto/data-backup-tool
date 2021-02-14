#!/usr/bin/python

import yaml
import os
import sys
from datetime import datetime
from datetime import timedelta


class Init:
    def __init__(self, settings=None):
        """
        Default constructor for the settings class
        :param settings: Path to the settings yaml file
        :raises ValueError if a nonexistent settings file is passed
        """
        if settings is None or not os.path.isfile(settings):
            print('Error: invalid settings file: {}'.format(settings))
            raise ValueError
        self.settings = settings

    @staticmethod
    def create_default_yaml():
        """
        Create a default settings file
        """
        settings = '../settings.yml.default'
        if os.path.isfile(settings):
            os.remove(settings)
        if not os.path.isfile(settings):
            config = """---
backup:
    target_dir:
    src_dir:
    rsnapshot:
        repo_dir:
        template_name: rsnapshot.conf.template
"""
            with open(settings, 'w', encoding='utf-8') as f:
                f.write(config)
            print('Default settings file created at {}'.format(os.path.abspath(settings)))

    def init(self):
        """
        Setup the backup folders and decide if a new full backup is needed.
        """
        with open(self.settings) as f:
            settings_yml = yaml.safe_load(f)

        date_format = '%Y-%m-%d_%H-%M-%S'
        backup_dir_name = settings_yml['backup']['latest']
        backup_dir_root = settings_yml['backup']['target_dir']
        backup_dir = os.path.join(backup_dir_root, backup_dir_name)
        cycle = settings_yml['backup']['full_backup_cycle']

        # Check if the backup target directory exists, abort if not
        if not os.path.isdir(backup_dir_root):
            print('Error: Backup destination {} cannot be found, please create it'
                  .format(backup_dir_root))
            exit(1)

        curr_time = datetime.now()
        name = curr_time.strftime(date_format)
        new_dir = os.path.join(backup_dir_root, name)

        # Check if the specified backup directory exists
        # if not, create a new one with a timestamp and a symlink to it
        if not os.path.isdir(backup_dir):
            os.makedirs(new_dir)
            os.symlink(new_dir, backup_dir)
        else:
            delta = timedelta(days=cycle['days'], hours=cycle['hours'],
                              minutes=cycle['minutes'], seconds=cycle['seconds'])
            # Get the time of the last full backup
            last_full_backup = os.readlink(backup_dir)
            last_time = datetime.strptime(os.path.basename(last_full_backup),
                                          date_format)

            # Check if a new full backup needs to be created
            if curr_time - last_time > delta:
                # Remove symlink to the last full backup
                os.remove(backup_dir)
                # Create new backup dir with the current time
                os.makedirs(new_dir)
                # Create a symlink to the new created directory
                os.symlink(new_dir, backup_dir)
        exit(0)


if __name__ == '__main__':
    if len(sys.argv) == 2:
        init = Init(sys.argv[1])
        init.init()
    else:
        print('Error: Please pass the path to the settings file as argument')
