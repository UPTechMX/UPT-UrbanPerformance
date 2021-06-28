# -*- coding: utf-8 -*-

import plup.Helpers.logging_config

def get_db():
    from django.db import connection
    return connection.cursor()

def get_uri():
    from django.db import connection as db
    return "postgresql://"+db.get_connection_params()['user'] +":"+ db.get_connection_params()['password'] +"@"+ db.get_connection_params()['host']+":"+ db.get_connection_params()['port'] +'/'+db.get_connection_params()['database']


def get_max_cores():
    from django.conf import settings
    return settings.PARALLEL["MAX_THREADS"]


def get_max_rows():
    from django.conf import settings
    return settings.PARALLEL["MAX_ROWS"]
