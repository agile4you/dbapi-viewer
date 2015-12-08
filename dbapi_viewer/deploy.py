# -*- coding: utf-8 -*-
"""`dbapi_viewer` package CLI interface.
"""


import click
import re
import bottle
from wsgi import dbviewer_service
from pgtools import PGPlugin


param_regex = re.compile(r"""
    \{
    (\w+)
    (?::([^}]+))?
    \}
    """, re.VERBOSE)


def uri_to_regex(template, param_sre=param_regex):
    """

    Args:
        template (str):
        param_sre (instance):

    Returns:

    """
    regex = ''
    last_pos = 0

    for match in param_sre.finditer(template):
        regex += re.escape(template[last_pos:match.start()])
        var_name = match.group(1)
        expr = match.group(2) or '[^/]+'
        expr = '(?P<%s>%s)' % (var_name, expr)
        regex += expr
        last_pos = match.end()
    regex += re.escape(template[last_pos:])
    regex = '^%s$' % regex
    return regex


POSTGRES_URI = re.compile(r"""
    ^(?P<user>[^/]+)@http:\/\/
     (?P<host>[^/]+):
     (?P<port>\d\d\d\d)
     \/(?P<database>[^/]+)
     \/(?P<password>[^/]+)$
     """, re.VERBOSE)


class ConnectionError(Exception):
    """Raise when postgres connection error occurs.
    """
    pass


def pg_connection(conn_str='', compiler_pattern=POSTGRES_URI):
    """Postgresql Database connection string compiler function.
    Compiles a connection string to a key/value pair.

    Args:
        conn_str (string): A valid postgres connection string.
        compiler_pattern (str): The class/type of the mapping

    Returns:
        A key/value pair of connection parameters.

    Raises:
        ConnectionError, when connection string is of invalid format.

    Examples:
        >>> import pprint
        >>> conn = 'db_user@http://db.server.com:6432/db011/my_secret'
        >>> pprint.pprint(pg_connection(conn_str=conn), depth=1, width=1)
        {'database': 'db011',
         'host': 'db.server.com',
         'password': 'my_secret',
         'port': 6432,
         'user': 'db_user'}
    """

    parsed_data = re.match(compiler_pattern, conn_str)

    if not parsed_data:
        raise ConnectionError("Invalid connection string.")

    results = parsed_data.groupdict()
    results['port'] = int(results.get('port'))

    return results


@click.command()
@click.option('-pg', '--postgres', default='',
              help='Postgres Connection string.')
@click.option('-h', '--host', default='localhost',
              help='Application server port.')
@click.option('-p', '--port', default='8081', help='Application server port.')
def deploy_service(postgres, host, port):
    """jhj
    """
    try:
        conn_info = pg_connection(conn_str=postgres)
    except ConnectionError, e:
        click.echo('Postgres connection error: {}'.format(e.args))
        return

    db = PGPlugin('db', **conn_info)

    version = db.version

    click.echo('\nChecking connectivity: ....\n')
    click.echo('Postgres Info: {}'.format(version))

    click.echo('dbapi-viewer server at: http://{}:{}'.format(host, port))

    dbviewer_service.install(db)

    bottle.debug(True)
    bottle.run(
        app=dbviewer_service,
        server='cherrypy',
        port=port,
        host=host,
        reloader=True
    )


if __name__ == '__main__':
    deploy_service()
