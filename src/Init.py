#!/usr/bin/python

import os
from datetime import datetime
from datetime import timedelta


class Init:
    def __init__(self, settings=None):
        """
        Default constructor for the settings class
        :param settings: Path to the settings yaml file
        :raises ValueError if a nonexistent settings file is passed
        """
        if settings is None:
            print('Error: No settings provided')
            raise ValueError
        self.date_format = '%Y-%m-%d_%H-%M-%S'
        self.settings = settings
        backup_dir_name = self.settings['backup']['latest']
        backup_dir_root = self.settings['backup']['target_dir']
        backup_dir = os.path.join(backup_dir_root, backup_dir_name)
        self.init(backup_dir, self.settings['backup']['full'], False)
        for i in self.settings['backup']['intervals']:
            backup_dir_int = os.path.join(backup_dir, i['name'])
            if not os.path.isdir(backup_dir_int):
                os.makedirs(backup_dir_int)

    def init(self, backup_dir, config, sync=False):
        """
        Setup the backup folders and decide if a new full backup is needed.
        """

        cycle = config['cycle']

        curr_time = datetime.now()
        name = curr_time.strftime(self.date_format)
        new_dir = os.path.join(os.path.dirname(backup_dir), name)

        # Check if the specified backup directory exists
        # if not, create a new one with a timestamp and a symlink to it
        if not os.path.isdir(backup_dir):
            os.makedirs(new_dir)
            os.symlink(os.path.basename(new_dir), backup_dir)
        else:
            delta = timedelta(days=cycle['days'], hours=cycle['hours'],
                              minutes=cycle['minutes'], seconds=cycle['seconds'])
            # Get the time of the last full backup
            last_full_backup = os.readlink(backup_dir)
            last_time = datetime.strptime(os.path.basename(last_full_backup),
                                          self.date_format)

            # Check if a new full backup needs to be created
            if curr_time - last_time > delta:
                # Remove symlink to the last full backup
                os.remove(backup_dir)
                # Create new backup dir with the current time
                self.new_dir(new_dir, sync)
                # Create a symlink to the new created directory
                os.symlink(os.path.basename(new_dir), backup_dir)

    def new_dir(self, new_dir, sync):
        if not sync:
            os.makedirs(new_dir)
