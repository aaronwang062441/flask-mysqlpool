#-*- coding: utf-8 -*-
import logging
import threading

import MySQLdb
import MySQLdb.connections
try:
    from flask import _app_ctx_stack as stack
except ImportError:
    from flask import _request_ctx_stack as stack


class Connection(MySQLdb.connections.Connection):

    def __init__(self, *args, **kwargs):
        super(Connection, self).__init__(*args, **kwargs)
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.debug('Initialing')


class ConnectionPool(object):

    def __init__(self, maxsize=0, **kwargs):
        self.log = logging.getLogger(self.__class__.__name__)

        self.log.debug('Initializing')

        self.maxsize = maxsize
        self._kwargs = kwargs

        self._lock = threading.Lock()
        self._not_empty = threading.Condition(self._lock)
        self._not_full = threading.Condition(self._lock)
        self._connections = []
        self._created = 0

    def get(self):
        self.log.debug('Getting a connection')
        conn = None
        self._not_empty.acquire()
        try:
            while not conn:
                if self._connections:
                    conn = self._connections.pop()
                elif (self.maxsize > 0 and self._created >= self.maxsize):
                    self._not_empty.wait()
                else:
                    self.log.debug('Creating a new connection')
                    self._connections.append(Connection(**self._kwargs))
                    self._created += 1
            self._not_full.notify()
            return conn
        finally:
            self._not_empty.release()

    def put(self, conn):
        self.log.debug('Returning the connection')
        self._not_full.acquire()
        try:
            if self.maxsize > 0:
                while len(self._connections) == self.maxsize:
                    self._not_full.wait()
            self._connections.append(conn)
            self._not_empty.notify()
        finally:
            self._not_full.release()


class MySQLPool(object):

    def __init__(self, app=None):
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.warning('Initializing')
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app):

        self.app.config.setdefault('MYSQL_POOL_SIZE', 0)
        self.app.config.setdefault('MYSQL_DATABASE_HOST', 'localhost')
        self.app.config.setdefault('MYSQL_DATABASE_PORT', 3306)
        self.app.config.setdefault('MYSQL_DATABASE_USER', '')
        self.app.config.setdefault('MYSQL_DATABASE_PASSWORD', '')
        self.app.config.setdefault('MYSQL_DATABASE_DB', '')
        self.app.config.setdefault('MYSQL_DATABASE_CHARSET', 'utf8')
        self.app.config.setdefault('MYSQL_USE_UNICODE', True)

        self.pool_size = self.app.config['MYSQL_POOL_SIZE']

        _argsmap = [('host', 'MYSQL_DATABASE_HOST'),
                    ('port', 'MYSQL_DATABASE_PORT'),
                    ('user', 'MYSQL_DATABASE_USER'),
                    ('passwd', 'MYSQL_DATABASE_PASSWORD'),
                    ('db', 'MYSQL_DATABASE_DB'),
                    ('charset', 'MYSQL_DATABASE_CHARSET'),
                    ('use_unicode', 'MYSQL_USE_UNICODE')]
        self.connect_args = dict()
        for k1, k2 in _argsmap:
            self.connect_args[k1] = self.app.config[k2]

        self.mysql_connpool = ConnectionPool(self.pool_size,
                **self.connect_args)

        if hasattr(app, 'teardown_appcontext'):
            app.teardown_appcontext(self.teardown)
        else:
            app.teardown_request(self.teardown)

    def teardown(self, exception):
        self.log.debug('teardown')
        ctx = stack.top
        if hasattr(ctx, 'current_connection') and ctx.current_connection:
            if exception:
                self.log.error('Rolling back since there was an exception')
                ctx.current_connection.rollback()
            else:
                self.log.debug('Commiting since no exception')
                ctx.current_connection.commit()
            self.mysql_connpool.put(ctx.current_connection)

    @property
    def connection(self):
        self.log.debug('Getting a connection')
        ctx = stack.top
        if ctx is not None:
            if not hasattr(ctx, 'current_connection') or not ctx.currect_connection:
                ctx.current_connection = self.mysql_connpool.get()
            return ctx.current_connection


