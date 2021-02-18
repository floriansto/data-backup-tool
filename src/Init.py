#!/usr/bin/python

import os
import util


class Init:
    def __init__(self, now, settings):
        """
        Default constructor for the settings class
        :param settings: Parsed configuration yaml file
        :param now: Current time as datetime object
        :raises ValueError if a nonexistent settings file is passed
        """
        self.date_format = settings['date_format']
        self.settings = settings
        self.now = now
        backup_dir_name = self.settings['latest']
        backup_dir_root = self.settings['target_dir']
        self.backup_dir = os.path.join(backup_dir_root, backup_dir_name)
        self.init(self.backup_dir, self.settings['full'])
        for i in self.settings['intervals']:
            backup_dir_int = os.path.join(self.backup_dir, i['name'])
            if not os.path.isdir(backup_dir_int):
                os.makedirs(backup_dir_int)

    def get_backup_target(self):
        """
        Return the path to the latest backup
        """
        return os.path.join(self.settings['target_dir'], os.readlink(self.backup_dir))

    def init(self, backup_dir, config):
        """
        Setup the backup folders and decide if a new full backup is needed.
        """

        cycle = config['cycle']

        name = self.now.strftime(self.date_format)
        new_dir = os.path.join(os.path.dirname(backup_dir), name)

        # Check if the specified backup directory exists
        # if not, create a new one with a timestamp and a symlink to it
        if not os.path.isdir(backup_dir):
            os.makedirs(new_dir)
            os.symlink(os.path.basename(new_dir), backup_dir)
        else:
            delta = util.t_delta_from_config(cycle)
            # Get the time of the last full backup
            last_full_backup = os.readlink(backup_dir)
            last_time = util.time_from_str(os.path.basename(last_full_backup),
                                           self.date_format)

            # Check if a new full backup needs to be created
            if self.now - last_time > delta:
                # Remove symlink to the last full backup
                os.remove(backup_dir)
                # Create new backup dir with the current time
                os.makedirs(new_dir)
                # Create a symlink to the new created directory
                os.symlink(os.path.basename(new_dir), backup_dir)
