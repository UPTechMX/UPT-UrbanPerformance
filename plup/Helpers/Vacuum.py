# -*- coding: utf-8 -*-
import sys
# sys.path.insert(1,"..")
import logging
import plup.Helpers.logging_config

class vacuum:
    def __init__(self, db, table, full=False):
        self.__logger = logging.getLogger(__name__)
        import psycopg2
        import psycopg2.extras
        self.conn = psycopg2.connect(db)
        try:
            self.cursor = self.conn.cursor(
                cursor_factory=psycopg2.extras.DictCursor)
            old_isolation_level = self.conn.isolation_level
            self.conn.set_isolation_level(0)
            if full:
                self.__query = "VACUUM (FULL,ANALYZE,VERBOSE) {table}".format(
                    table=table)
            else:
                self.__query = "VACUUM (ANALYZE,VERBOSE) {table}".format(table=table)
            self.__logger.debug(dict(table=table,query=self.__query))
            self.cursor.execute(self.__query)
            self.conn.commit()
            self.conn.set_isolation_level(old_isolation_level)
        except Exception as e:
            self.conn.rollback()
            self.conn.close()
            self.__logger.debug(dict(table=table,query=self.__query, code=e))
        else:
            self.conn.close()
            self.__logger.debug(dict(table=table,query=self.__query))


def selfexit():
    import sys
    sys.exit(0)


if __name__ == '__main__':
    import sys
    import os
    import signal
    import time
    my_pid = os.getpid()
    logger = logging.getLogger(__name__)
    signal.signal(signal.SIGINT, selfexit)

    # sys.argv[1] connection uri
    # # option 1 evaluates the provided scenatios
    # sys.argv[2] table
    # sys.argv[3] user id
    logger.debug(dict(process_id=my_pid,args=sys.argv))
    if len(sys.argv) <= 1:
        logger.debug(dict(args=len(sys.argv),message="You must provide argumentes"))
    elif (len(sys.argv) == 4 and sys.argv[3] == '1'):
        vacuum(sys.argv[1], sys.argv[2])
