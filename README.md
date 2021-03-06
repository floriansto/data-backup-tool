# Data Backup Tool (DBT)

The DBT is a centralized approach to backup your data from any linux PC to a central linux driven server.
The tool should run on your central machine where you want to store your data.

Backups to the same machine (or to a connected external drive) are also possible.

## Backups
After a given interval (or when starting fresh) a new full backup is created.
Between the full backups the tool creates incremental backups for faster speeds. Only changed files are transferred.

Every backup (snapshot and full) contains the whole folderstructure of the included files.
To achieve this for the snapshots, hardlinks are used.
Disadvantage is, that files that do not change are only stored on time on the disk.
If this file is damaged, it is damaged in all incremetal backups.
To keep this risk low full backups are performed after a configured interval.

## Configuration
The configuration file needs the following layout:
```yaml
target_dir: 'backup_destination_without_trailing_slash'
latest: 'latest'
src:
  - '/'
exclude:
  - '*'
date_format: '%Y-%m-%d_%H-%M-%S'
full:
  cycle:
    days: 90
    hours: 0
    minutes: 0
    seconds: 0
intervals:
  - name: hourly
    prio: 4
    num: 20
    cycle:
      days: 0
      hours: 1
      minutes: 0
      seconds: 0
```
### target_dir
The `target_dir` is the directory where the backup is stored.
**Important: Trailing slashes are ignored.**

### latest
Name of the symlink to the newest backup

### src
Array of source files and folders

### exclude
Exclude patterns which should not be in the backup

### date_format
Date format for the backup folders

### full
Configuration for the full backup.

### intervals
Array of intervals for the incremental backups.
`num` specifies the number of backups to store.
If this number is exceeded, the oldest backup gets deleted before a new backup is created.

The `prio` defines the priority of the interval.
Backups are performed from the interval with the highest prio to the lowest.
Backups with the shortest interval should have the highest priority.

## Folder structure
The generated folder structure can look like
```
|- 2020-01-01_22-32-54
|  |
|  +- hourly
|  |  |
|  |  +- 2020-01-01-22-32-54
|  |  +- 2020-01-01-23-32-54
|  |  +- latest --> 2020-01-01-23-32-54
|  +- daily
|     |
|     +- 2020-01-01-22-32-54
|     +- 2020-01-02-22-32-54
|     +- latest --> 2020-01-02-22-32-54
+- latest --> 2020-01-01_22-32-54
```
The first level represent full backups, all unterlying levels are incremental snapshots.

## Required tools
The following packages are neede:
- rsync
- cp
- python >= 3.8
- python-pip

## Python requirements
The following packages are used
- click
- shutil
- pyyaml

# Usage
To get an overview of all options run
```sh
./src/main.py --help
```
The tool is called using
```sh
./src/main.py [OPTIONS] CONFIG
```
where `CONFIG` specifies your configuration file.

## Options
```
  -s, --ssh           Use ssh connection to get backup files
  -h, --host TEXT     When using ssh, connect to this host. May be hostname or
                      ip adress

  -p, --port INTEGER  When using ssh, use this port
  -u, --user TEXT     When using ssh, use this user
  -n, --no-relatives  Do not use relative path names. Disables the -R option
                      of rsync.

  -v, --verbose       Additional output to the logfile
  --help              Show this message and exit.
```

## SSH connection
When you use the ssh connection make sure that your backup machine has access to your given host.
Currently you can only sync from a remote machine to a local machine and **not** the other way around.

## Logging
Logs are stored under `/var/log/dbt/` with the naming scheme `backup_HOST.log`.
On every run a new file is created. The last 10 files are kept.

# Todo
- Sending email on failure
- Do backup to remote machine

