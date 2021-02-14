#!/usr/bin/python

import os
from datetime import datetime

class Backup:
    def __init__(self, settings, backup_dir, now):
        self.settings = settings
        self.now = now
        self.intervals = []
        self.backup_dir = backup_dir
        self.sort_intervals()
        if self.all_new():
            self.init_backup()

    def sort_intervals(self):
        used_idx = []
        intervals = self.settings['backup']['intervals']
        for i in range(len(intervals)):
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

    def all_new(self):
        highest_prio_dir = os.path.join(self.backup_dir, self.intervals[0]['name'], self.settings['backup']['latest'])
        ret = not os.path.exists(highest_prio_dir)
        return ret

    def init_backup(self):
        high_prio = self.intervals[0]
        high_prio_dir = os.path.join(self.backup_dir, high_prio['name'])
        new_backup = os.path.join(high_prio_dir, self.now.strftime(self.settings['backup']['date_format']))
        new_backup_link = os.path.join(high_prio_dir, self.settings['backup']['latest'])
        os.makedirs(new_backup)
        os.symlink(os.path.basename(new_backup), new_backup_link)

        print('Rsync to {} latest'.format(high_prio['name']))

        for i in range(1, len(self.intervals)):
            print('Create hardlink from {} to {}'.format(self.intervals[i-1]['name'], self.intervals[i]['name']))
            print('Create latest symlink')

