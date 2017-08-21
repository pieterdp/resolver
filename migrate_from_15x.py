#!/usr/bin/env python2.7
import argparse
import subprocess
import getpass
from resolver.database import db, app


def conn():
    return db.session.connection()


def backup(user, password, database):
    c = [
        'mysqldump',
        '-u',
        user,
        '-p',
        password,
        database
    ]
    o = subprocess.check_output(c)
    with open('./backup.sql', 'w') as fh:
        fh.write(o)


def update(table='user'):
    r = db.engine.execute('SHOW COLUMNS FROM `{0}`;'.format(table))
    if 'auth_token' not in [c[0] for c in r]:
        db.engine.execute('ALTER TABLE `{0}` ADD `auth_token` VARCHAR(256);'.format(table))
    db.engine.execute('ALTER TABLE `{0}` MODIFY `username` VARCHAR(64);'.format(table))
    db.engine.execute('ALTER TABLE `{0}` MODIFY `password` VARCHAR(256);'.format(table))


def main():
    parser = argparse.ArgumentParser(description='Update the database to 1.7.2.')
    parser.add_argument('--no_backup', action='store_true', help='Do not backup the database first.')
    args = parser.parse_args()
    print('This script will perform the required database modifications to update from')
    print('the 1.5.x branch to the current 1.7.2 release.')
    print('Note that the password algorithm changed as well, so you will have to reset')
    print('all passwords. This script will not do that.')
    print('Performing database backup ...')
    if not args.no_backup:
        try:
            backup(app.config['DATABASE_USER'], app.config['DATABASE_PASS'], app.config['DATABASE_NAME'])
        except Exception as e:
            print('[failed]')
            print(e)
            return 1
        else:
            print('[ok]')
    print('Performing upgrade ...')
    try:
        update()
    except Exception as e:
        print('[failed]')
        print(e)
        return 2
    else:
        print('[ok]')
    return 0


if __name__ == '__main__':
    exit(main())
