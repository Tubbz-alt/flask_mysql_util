import pymysql
import os
from flask import _request_ctx_stack


CONFIG_KEYS = {'_DATABASE_HOST': 'localhost', '_DATABASE_PORT': 3306, '_DATABASE_USER': None, '_DATABASE_PASSWORD': None, '_DATABASE_DB': None, '_DATABASE_CHARSET': 'utf8', '_DATABASE_USE_UNICODE': True}

class MultiMySQL(object):
    """
    Extension of the classic MySQL Flask extension to be able to handle multiple databases from a single FLASK app.
    Create a MultiMySQL with a prefix; for example LOGBOOK.
    This then looks in the environmnent for for database connection strings. 
    <prefix>_DATABASE_HOST
    <prefix>_DATABASE_PORT
    <prefix>_DATABASE_USER
    <prefix>_DATABASE_PASSWORD
    <prefix>_DATABASE_DB
    <prefix>_DATABASE_CHARSET
    <prefix>_DATABASE_USE_UNICODE
    If your application has a context object, construct it in the context and call init_app in the start.py
    Gathers the configuration from os.environ and puts in the Flask application context.
    :param prefix - The string prefix that identifies the database configuration for this connection in the os.environ.
    :param app - The flask application (if you have access to it)
    :param connect_args - args passed to MySQLdb
    """
    def __init__(self, prefix, app=None, **connect_args):
        self.connect_args = connect_args
        self.prefix = prefix
        self.config = {}
        for config_key, default_val in CONFIG_KEYS.items():
            self.config.setdefault(self.prefix + config_key, os.environ.get(self.prefix + config_key, default_val))
        if app is not None:
            self.app = app
            self.init_app(self.app)
        else:
            self.app = None

    def init_app(self, app):
        '''
        Register before and teardown callbacks with the Flask application.
        '''
        self.app = app               
        self.app.teardown_request(self.teardown_request)
        self.app.before_request(self.before_request)

    def get_db(self):
        '''Get the database connection for this request'''
        ctx = _request_ctx_stack.top
        if ctx is not None:
            return ctx.mysql_cons[self.prefix]
        
    def connect(self):
        '''Establishes the actual connection'''
        if self.config[self.prefix + '_DATABASE_HOST']:
            self.connect_args['host'] = self.config[self.prefix + '_DATABASE_HOST']
        if self.config[self.prefix + '_DATABASE_PORT']:
            self.connect_args['port'] = self.config[self.prefix + '_DATABASE_PORT']
        if self.config[self.prefix + '_DATABASE_USER']:
            self.connect_args['user'] = self.config[self.prefix + '_DATABASE_USER']
        if self.config[self.prefix + '_DATABASE_PASSWORD']:
            self.connect_args['passwd'] = self.config[self.prefix + '_DATABASE_PASSWORD']
        if self.config[self.prefix + '_DATABASE_DB']:
            self.connect_args['db'] = self.config[self.prefix + '_DATABASE_DB']
        if self.config[self.prefix + '_DATABASE_CHARSET']:
            self.connect_args['charset'] = self.config[self.prefix + '_DATABASE_CHARSET']
        if self.config[self.prefix + '_DATABASE_USE_UNICODE']:
            self.connect_args['use_unicode'] = self.config[self.prefix + '_DATABASE_USE_UNICODE']
        return MySQLdb.connect(**self.connect_args)

    def before_request(self):
        '''Flask before request callback'''
        ctx = _request_ctx_stack.top
        if hasattr(ctx, 'mysql_cons'):
            ctx.mysql_cons[self.prefix] = self.connect()
        else:
            ctx.mysql_cons = {self.prefix: self.connect()}

    def teardown_request(self, exception):
        '''Flask after request teardown for closing the connection'''
        ctx = _request_ctx_stack.top
        if hasattr(ctx, 'mysql_cons'):
            ctx.mysql_cons[self.prefix].close()

