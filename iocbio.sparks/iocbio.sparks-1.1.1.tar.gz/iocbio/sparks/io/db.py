# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
#  Copyright (C) 2018
#   Laboratory of Systems Biology, Department of Cybernetics,
#   School of Science, Tallinn University of Technology
#  Authors: Martin Laasmaa and Marko Vendelin
#  This file is part of project: IOCBIO Sparks
#
from PyQt5.QtWidgets import QDialog, QLineEdit, QPushButton, QGridLayout, QMessageBox, QLabel, QCheckBox, QFileDialog
from PyQt5.QtCore import QSettings
from collections import OrderedDict
import os, sys, traceback

from iocbio.sparks.constants import application_name


def mkdir_p(path):
    import errno
    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise


class Login(QDialog):
    def __init__(self):
        QDialog.__init__(self)
        self.setWindowTitle("PostgreSQL login")
        self.textName = QLineEdit(self)
        self.textPass = QLineEdit(self)
        self.textPass.setEchoMode(QLineEdit.Password)
        self.buttonLogin = QPushButton('Login', self)
        self.buttonLogin.clicked.connect(self.handleLogin)
        self.rememberPassword = QCheckBox("Store password in keyring")
        self.rememberPassword.setCheckState(False)
        layout = QGridLayout(self)
        layout.addWidget(QLabel("User:"), 0, 0)
        layout.addWidget(self.textName, 0, 1)
        layout.addWidget(QLabel("Password:"), 1, 0)
        layout.addWidget(self.textPass, 1, 1)
        layout.addWidget(self.buttonLogin,2,1)
        layout.addWidget(self.rememberPassword,3,1)

    def handleLogin(self):
        self.username = self.textName.text()
        self.password = self.textPass.text()
        self.accept()


class DatabaseInterface:
    """Database interface and helper functions"""

    schema_version = "6"
    database_table = "iocbio"

    settings_dbtype = "database/type"

    settings_pg_hostname = "database/postgresql/hostname"
    settings_pg_database = "database/postgresql/database"
    settings_pg_schema = "database/postgresql/schema"
    settings_pg_username = "database/postgresql/username"

    username = None
    password = None

    def __init__(self):
        settings = QSettings()

        self.dbtype = str(settings.value(DatabaseInterface.settings_dbtype, "sqlite3"))
        self.read_only = False
        self.disable_read_only = False # not needed here, but keeping for completeness

        self.connection_parameters = OrderedDict()
        self.database = None

        self.debug_sql = (int(settings.value("database/debug", 0)) > 0)

        if self.dbtype == "sqlite3":
            self.open_sqlite3()
        elif self.dbtype == "postgresql":
            self.open_postgresql()
        else:
            raise NotImplementedError("Not implemented: " + self.dbtype)

        if self.database is not None:
            self.schema()

    def __del__(self):
        self.close()

    def set_read_only(self, state):
        if self.disable_read_only:
            self.read_only = False
        else:
            self.read_only = state

    def open_sqlite3(self):
        from PyQt5.QtCore import QStandardPaths
        import sqlite3

        path = QStandardPaths.writableLocation(QStandardPaths.AppDataLocation)
        mkdir_p(path)
        fname = os.path.join(path,"sparks.sqlite")

        self.database = sqlite3.connect(os.path.join(path,"sparks.sqlite"))
        self.database.row_factory = sqlite3.Row

        # self.database = Database("sqlite:///" + fname)

        # require foreign key constraints to be followed
        self.query("PRAGMA foreign_keys=ON")

        # save parameters
        self.connection_parameters['Database connection type'] = 'SQLite3'
        self.connection_parameters['File name'] = fname

    def open_postgresql(self):
        from records import Database
        import keyring

        keyring_key = "iocbio-sparks"
        save = False

        settings = QSettings()

        self.pg_hostname = str(settings.value(DatabaseInterface.settings_pg_hostname, ""))
        self.pg_database = str(settings.value(DatabaseInterface.settings_pg_database, ""))
        self.pg_schema = str(settings.value(DatabaseInterface.settings_pg_schema, ""))

        if len(self.pg_hostname)<1 or len(self.pg_database)<1 or len(self.pg_schema)<1:
            QMessageBox.warning(None, 'Error',
                                "Failed to open PostgreSQL database connection\nEither hostname, database, or schema not specified")
            return

        if DatabaseInterface.username is None:
            username = str(settings.value(DatabaseInterface.settings_pg_username, defaultValue = ""))
            try:
                password = keyring.get_password(keyring_key, username)
            except:
                print('Failed to get password from keyring, assuming that it is not available')
                password = None

            if len(username) < 1 or password is None:
                login = Login()
                if login.exec_() == QDialog.Accepted:
                    username = login.username
                    password = login.password
                    save = login.rememberPassword.checkState()
                else:
                    return
        else:
            username = DatabaseInterface.username
            password = DatabaseInterface.password

        try:
            self.database = Database("postgresql://" + username + ":" + password +
                                     "@" + self.pg_hostname + "/" + self.pg_database)
            DatabaseInterface.username = username
            DatabaseInterface.password = password
        except Exception as expt:
            if not save:
                # probably wrong uid/pwd, cleanup
                settings.setValue(DatabaseInterface.settings_pg_username, "")
                try:
                    keyring.delete_password(keyring_key, username)
                except:
                    print('Faild to delete password from keyring')
            print('Exception', expt)
            QMessageBox.warning(None, 'Error',
                                "Failed to open PostgreSQL database connection\n\nException: " + str(expt))
            self.database = None

        if save:
            # let's save the settings
            settings.setValue(DatabaseInterface.settings_pg_username, username)
            try:
                keyring.set_password(keyring_key, username, password)
            except Exception as e:
                errtxt = '\nError occurred while saving password to the keyring:\n\n' + str(e) + "\n\n" + str(type(e))
                print(errtxt + '\n\n')
                print(traceback.format_exc())
                QMessageBox.warning(None, 'Warning',
                                    "Failed to save password in a keyring")

        # store connection parameters
        self.connection_parameters['Database connection type'] = 'PostgreSQL'
        self.connection_parameters['Host name'] = self.pg_hostname
        self.connection_parameters['Database'] = self.pg_database
        self.connection_parameters['Schema'] = self.pg_schema
        self.connection_parameters['User'] = username

    def close(self):
        if self.database is not None:
            if self.dbtype == "sqlite3":
                self.database.commit()
            self.database.close()
            self.database = None

    def query(self, command, **kwargs):
        if self.read_only:
            for k in ['insert ', 'create ', 'update ', 'set ', 'delete ']:
                if k in command.lower():
                    return None

        if self.debug_sql:
            print(command, kwargs)

        if self.dbtype == "sqlite3":
            c = self.database.cursor()
            return c.execute(command, kwargs).fetchall()

        # the rest goes via records
        return self.database.query(command, **kwargs)

    def schema(self):
        """Check the present schema version, create if missing and return the version of current schema"""

        tname = self.table(DatabaseInterface.database_table)
        self.query("CREATE TABLE IF NOT EXISTS " + tname + "(name text NOT NULL PRIMARY KEY, value text NOT NULL)")

        version = None
        for row in self.query("SELECT value FROM " + tname + " WHERE name=:name", name = "sparks_version"):
            version = row[0]

        if version is None:
            self.query("INSERT INTO " + tname + "(name, value) VALUES(:name,:val)",
                       name = "sparks_version", val = DatabaseInterface.schema_version)
            version = DatabaseInterface.schema_version

        if version == "1":
            self.schema_update_1_2()
        elif version == "2":
            self.schema_update_2_3()
        elif version == "3":
            self.schema_update_3_4()
        elif version == "4":
            self.schema_update_4_5()
        elif version == "5":
            self.schema_update_5_6()
        elif version == "6":
            pass
        else:
            raise RuntimeError("This version (%s) of database schema is not supported" % version)

    def schema_update_1_2(self):
        from iocbio.sparks.constants import database_table_experiment

        if self.read_only:
            raise RuntimeError("Cannot update database schema in read only mode")

        self.query("ALTER TABLE " + self.table(database_table_experiment) +
                   " ADD transposed INTEGER DEFAULT 0")
        self.query("UPDATE " + self.table(DatabaseInterface.database_table) + " SET value=:val WHERE name=:name",
                   name = "sparks_version", val = "2")

        self.schema() # to check whether further updates are needed

    def schema_update_2_3(self):
        from iocbio.sparks.calc.spark import Spark

        if self.read_only:
            raise RuntimeError("Cannot update database schema in read only mode")

        Spark.database_schema_update_2_3(self)
        self.query("UPDATE " + self.table(DatabaseInterface.database_table) + " SET value=:val WHERE name=:name",
                   name = "sparks_version", val = "3")

        self.schema() # to check whether further updates are needed

    def schema_update_3_4(self):
        from iocbio.sparks.constants import database_table_experiment
        from iocbio.sparks.calc.spark import Spark
        from iocbio.sparks.handler.image import Image

        if self.read_only:
            raise RuntimeError("Cannot update database schema in read only mode")

        Image.database_schema_update_3_4(self)
        Spark.database_schema_update_3_4(self)
        self.query("UPDATE " + self.table(DatabaseInterface.database_table) + " SET value=:val WHERE name=:name",
                   name = "sparks_version", val = "4")

        self.schema() # to check whether further updates are needed

    def schema_update_4_5(self):
        from iocbio.sparks.constants import database_table_experiment
        from iocbio.sparks.handler.image import Image

        if self.read_only:
            raise RuntimeError("Cannot update database schema in read only mode")

        Image.database_schema_update_4_5(self)
        self.query("UPDATE " + self.table(DatabaseInterface.database_table) + " SET value=:val WHERE name=:name",
                   name = "sparks_version", val = "5")

        self.schema() # to check whether further updates are needed

    def schema_update_5_6(self):
        from iocbio.sparks.constants import database_table_experiment
        from iocbio.sparks.handler.image import Image

        if self.read_only:
            raise RuntimeError("Cannot update database schema in read only mode")

        Image.database_schema_update_5_6(self)
        self.query("UPDATE " + self.table(DatabaseInterface.database_table) + " SET value=:val WHERE name=:name",
                   name = "sparks_version", val = "6")

        self.schema() # to check whether further updates are needed

    def table(self, name, with_schema=True):
        # IF CHANGED HERE, CHECK OUT also the following methods
        #   has_view
        if self.dbtype == "sqlite3": return name
        elif self.dbtype == "postgresql":
            if with_schema: return self.pg_schema + ".sparks_" + name
            else: return "sparks_" + name
        else:
            raise NotImplementedError("Not implemented table name mangling: " + self.dbtype)

    def get_table_column_names(self, name):
        for c in self.query("SELECT * FROM %s LIMIT 1" % self.table(name)):
            return c.keys()
        return None

    def has_record(self, table, **kwargs):
        a = []
        sql = "SELECT 1 FROM " + self.table(table) + " WHERE "
        for key in kwargs.keys():
            sql += key + "=:" + key + " AND "
        sql = sql[:-5] # dropping excessive " AND "
        sql += " LIMIT 1"
        for row in self.query(sql, **kwargs):
            return True
        return False

    def has_view(self, view):
        if self.dbtype == "sqlite3":
            for row in self.query("SELECT 1 AS reply FROM sqlite_master WHERE type='view' AND " +
                                  "name=:view", view=self.table(view)):
                return True
        elif self.dbtype == "postgresql":
            for row in self.query("SELECT 1 AS reply FROM information_schema.views WHERE " +
                                  "table_schema=:schema AND table_name=lower(:view)",
                                  schema=self.pg_schema, view=self.table(view, with_schema=False)):
                return True
        else:
            raise NotImplementedError("Not implemented table name mangling: " + self.dbtype)

        return False

    @property
    def is_ok(self):
        return self.database is not None
