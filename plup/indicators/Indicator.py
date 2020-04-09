# -*- coding: utf-8 -*-
import os
import logging
import plup.Helpers.logging_config
import plup.Helpers.config as config


class Indicator:
    def __init__(self, user):
        self.__db = config.get_db()
        self.__uri = config.get_uri()
        self.__max_threads = int(config.get_max_cores())
        self.__max_rows = float(config.get_max_rows())
        self.__user = user
        self.__split_uri()

    def __split_uri(self):
        parts = self.__uri.split(":")
        self.__db_user = parts[1].split("//")[1]
        self.__db_host = parts[2].split("@")[1]
        self.__db_port = parts[3].split("/")[0]
        self.__db_passw = parts[2].split("@")[0]
        self.__db_dbname = parts[3].split("/")[1]

    def get_uri(self):
        return self.__uri

    def close_connection(self):
        self.__db.close()

    def get_up_calculator_connection(self):
        return self.__db

    def get__up_calculator_user(self):
        return self.__db_user

    def get__up_calculator_host(self):
        return self.__db_host

    def get__up_calculator_port(self):
        return self.__db_port

    def get__up_calculator_passw(self):
        return self.__db_passw

    def get__up_calculator_dbname(self):
        return self.__db_dbname

    def get_max_threads(self):
        return self.__max_threads

    def get_max_rows(self):
        return self.__max_rows

    def get_user(self):
        return self.__user
