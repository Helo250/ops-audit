# -*- coding: utf-8 -*-
# Filename: migrations
# Author: brayton
# Datetime: 2019-Oct-14 2:42 PM

import os

os.environ['SANIC_SETTINGS_MODULE'] = '/home/brayton/IdeaProjects/cmdb_audit/setting'

from core.migrations import MigrationModel, db_manager
from platforms.cmdb.models import LoginLog, FTPLog
from peewee import CharField
from playhouse.migrate import migrate


class LoginLogMigration(MigrationModel):
    _model = LoginLog

    def migrate_drop_column(self):
        migrate(
            self.drop_column('cmdb_uid'),
        )

    def migrate_add_column(self):
        migrate(
            self.add_column('city', CharField(verbose_name='client address city', default='')),
        )

    def migrate_change_column(self):
        migrate(
            self.rename_column('ip', 'remote_addr'),
            self.rename_column('agent', 'user_agent')
        )


class FTPLogMigration(MigrationModel):
    _model = FTPLog

    def migrate_drop_column(self):
        migrate(
            self.drop_column('cmdb_uid'),
        )

    def migrate_add_column(self):
        migrate(
            self.add_column('city', CharField(verbose_name='client address city', default='')),
        )

    def migrate_change_column(self):
        migrate(
            self.rename_column('ip', 'remote_addr'),
        )


def make_migration():
    login_log = LoginLogMigration()
    ftp_log = FTPLogMigration()
    with db_manager.transaction():
        login_log.auto_migrate()
        ftp_log.auto_migrate()
    print('successfully')


if __name__ == '__main__':
    make_migration()
