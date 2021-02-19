#!/usr/bin/python

import os
import util
import logging
import subprocess


logger = logging.getLogger('backup')

class Backup:
    def __init__(self, settings, backup_dir, now):
        self.settings = settings
        self.date_format = settings['date_format']
        self.now = now
        self.intervals = []
        self.backup_dir = backup_dir
        self.sort_intervals()
        self.highest_prio_backup()
        self.lower_prio_backups()

    def sort_intervals(self):
        """
        Sort the configured intervals by their priority from
        high to low.
        """
        used_idx = []
        intervals = self.settings['intervals']
        for _ in range(len(intervals)):
            highest_prio = -1
            highest_prio_idx = 0
            found = False
            for idx, i in enumerate(intervals):
                if i['prio'] > highest_prio and idx not in used_idx:
                    highest_prio = i['prio']
                    highest_prio_idx = idx
                    found = True
            if found:
                self.intervals.append(intervals[highest_prio_idx])
                used_idx.append(highest_prio_idx)
        logger.info('Intervals from high to low priority: {}'.format(', '.join([i['name'] for i in self.intervals])))

    def prepare_backup(self, interval):
        """
        Preparing the current interval for the backup.
        Do the following:
        - Check if the timedelta between the last backup and now exceeds
          the configured backup cycle.
        - If not, do nothing
        - If yes:
            - If the number of existing backups is larger or equal to the
              configured number of backups, recycle the oldest backup, else
              create a new folder and hardlink the latest backup to it
            - Let the latest symlink point to the newly created folder
        :param interval: Configuration for the selected interval
        :return: True if a backup should be done
        """
        logger.debug('Preparing for backup')
        delta = util.t_delta_from_config(interval['cycle'])
        backup_dir = os.path.join(self.backup_dir, interval['name'])
        latest = os.path.join(backup_dir, self.settings['latest'])
        if os.path.exists(latest):
            t_latest = util.time_from_str(os.path.basename(os.readlink(latest)), self.date_format)
        else:
            t_latest = util.time_from_str('0', '%S')

        # Check if the timedelta between the last backup and now exceeds
        # the configured maximum
        if self.now - t_latest < delta:
            logger.info('Skip {} backup'.format(interval['name']))
            logger.debug('Timedelta between last {} backup and now is too narrow for a new backup.'.format(interval['name']))
            logger.debug('Next backup will be possible at {}'.format((self.now + delta).strftime(self.date_format)))
            return False

        # Get a list of all backups for the selected interval
        folders = os.listdir(backup_dir)
        folders = [os.path.join(backup_dir, i) for i in folders]
        # Do only include folders
        folders_filtered = [i for i in folders if (os.path.isdir(i) and not os.path.islink(i))]
        new_folder = os.path.join(backup_dir, self.now.strftime(self.date_format))
        # Choose action based on the number of existing backups
        if len(folders_filtered) >= interval['num']:
            # More or equal backups exist: Recycle the oldest backup
            folder_from = sorted(folders_filtered)[0]
            logger.debug('Rename {} to {}'.format(folder_from, new_folder))
            # Rename oldest backup
            os.system('mv {} {}'.format(folder_from, new_folder))
            # Update it to the newest state
            sync_src = latest.rstrip('/') + '/*'
            logger.debug('Hardlink new files from {}'.format(sync_src))
            os.system('cp -urldf {} {}'.format(sync_src, new_folder))
        elif len(folders_filtered) == 0:
            # No backups exist: Create a new folder
            os.makedirs(new_folder)
        else:
            # Less backups exist: Hardlink from the latest backup to the new backup
            folder_from = sorted(folders_filtered)[-1]
            logger.debug('Hardlink from {} to new backup {}'.format(folder_from, new_folder))
            os.system('cp -urldf {} {}'.format(folder_from, new_folder))
        if os.path.exists(latest):
            os.remove(latest)
        os.symlink(os.path.basename(new_folder), latest)
        return True

    def highest_prio_backup(self):
        """
        Create a backup for the highest priority.
        Therefore call rsync to sync from the specified backup directories to the latest backup folder
        """
        interval = self.intervals[0]
        ret = self.prepare_backup(interval)
        latest = self.settings['latest']
        if ret:
            logger.info('Start {} backup'.format(interval['name']))
            dest = os.path.join(self.backup_dir, interval['name'], latest).rstrip('/')
            rels = 'R' if not self.settings['no_rels'] else ''
            # Build string for the ssh connection if needed
            if self.settings['ssh']:
                ssh = ['-e', 'ssh -p {}'.format(self.settings['port'])]
                src = '{}@{}:'.format(self.settings['user'], self.settings['host'])
                src_div = ' :'
            else:
                ssh = []
                src = ''
                src_div = ' '
            src += src_div.join(self.settings['src'])
            # Build exclude patterns
            if self.settings['exclude'] is not None:
                exclude = '--exclude="' + '" --exclude="'.join(self.settings['exclude']) + '"'
            else:
                exclude = ''
            # Build command for the subprocess call
            arg = 'rsync -rahs{} -zz --no-perms --info=progress2 --delete-excluded --delete {}'\
                .format(rels, exclude)
            cmd = arg.split(' ')
            cmd += ssh
            cmd += src.split(' ')
            cmd += [dest]
            logger.debug('Run command: {}'.format(arg))
            ret = subprocess.run(cmd, stderr=subprocess.PIPE)
            # Check for errors
            if ret.returncode != 0:
                logger.error('Rsync exited with  {}'.format(ret.returncode))
                logger.error(' '.join(ret.args))
                logger.error(ret.stderr)
                logger.error('Aborting backup')
                raise subprocess.CalledProcessError(returncode=ret.returncode, cmd = ret.args, stderr = ret.stdout)
            logger.info('Finished {} backup'.format(interval['name']))

    def lower_prio_backups(self):
        """
        Do backups for the lower priority backups.
        If the time interval is reached, create hardlinks from the latest backup with the highest priority to a
        new backup of the selected priority
        """
        latest = self.settings['latest']
        src = os.path.join(self.backup_dir, self.intervals[0]['name'], latest).rstrip('/')
        for i in range(len(self.intervals) - 1):
            interval = self.intervals[i + 1]
            ret = self.prepare_backup(interval)
            if ret:
                logger.info('Start {} backup'.format(interval['name']))
                dest = os.path.join(self.backup_dir, interval['name'], latest).rstrip('/')
                src_sync = src.rstrip('/') + '/*'
                logger.debug('Hardlink from {} to {}'.format(src_sync, dest))
                os.system('cp -urldf {} {}'.format(src_sync, dest))
                logger.info('Finished {} backup'.format(interval['name']))
