#!/usr/bin/env python
import argparse
import subprocess
import getpass
from resolver.database import app, db


def conn():
    return db.session.connection()


def backup(user, password, table):
    c = [
        'mysqldump',
        '-u',
        user,
        '-p',
        password,
        table
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


def update_password():
    pass


def main():
    parser = argparse.ArgumentParser(description='Update from 1.5.x')
    parser.add_argument('--user', default='root')
    parser.add_argument('--table', default='resolver')
    arguments = parser.parse_args()
    password = getpass.getpass('MySQL password: ')


if __name__ == '__main__':
    exit(main())
