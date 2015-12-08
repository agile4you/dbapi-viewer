# -*- coding: utf-8 -*-
"""`dbapi_viewer.pgtools` module.

Provides basic Postgresql utilities for translating HTTP parameters to Database
API (UDF/Views) call.
"""

__license__ = 'GLPv3'
__date__ = '13-11-2015'
__author__ = 'Papavassiliou Vassilis'
__version__ = '0.0.1'
__all__ = ['PGPlugin', 'api_compiler', 'FunctionParamError']


import bottle
import inspect
import os
import psycopg2
import psycopg2.extras
from psycopg2.extras import RealDictCursor

# Try to find the best candidate for JSON serialization.
# Import order indicates serialization efficiency.


SQL_DIR =  '/'.join(os.path.abspath(__file__).split('/')[:-1])


try:
    import simplejson as json
except ImportError:
    import json


class FunctionParamError(Exception):
    """Raises when invalid type parameter is passed to Postgresql Function.
    """
    pass


class BaseFuncArg(object):
    """**Base Postgresql Function parameter validator**

    Implements a base validator template class for function parameters.
    Subclass it and define the attributes.


    Attributes:
        - formatter (str): The string template corresponding to DB native form.
        - param_type (tuple): The parameter native classes allowed.
    """

    formatter = ''
    param_type = None

    def __init__(self, param):
        self.param = param

    def validate(self):
        if not isinstance(self.param, self.param_type):
            raise FunctionParamError(
                "Invalid type for {} param".format(self.param_type)
            )
        return self.formatter.format(
            self.format()
        )

    def format(self):
        return self.param


class NumArg(BaseFuncArg):
    """Numeric Parameters formatter/validator class.
    """
    formatter = '{}'
    param_type = (int, float)


class TextArg(BaseFuncArg):
    """Textual Parameters formatter/validator class.
    """
    formatter = "'{}'"
    param_type = (str, buffer, unicode)


class BooleanArg(BaseFuncArg):
    """Boolean Parameters formatter/validator class.
    """
    formatter = "{}"
    param_type = (bool, )

    def format(self):
        return str(self.param).upper()


class ArrayArg(BaseFuncArg):
    """Array Parameters formatter/validator class.
    """
    formatter = "'{}'"
    param_type = (list, tuple)

    def format(self):
        array_data = str(self.param)[1:-1].replace("u'", "").replace("'", '')
        return '{%s}' % array_data


class JSONArg(BaseFuncArg):
    """JSON Parameters formatter/validator class.
    """
    formatter = "'{}'"
    param_type = (dict, )

    def format(self):
        return json.dumps(self.param)


FUNC_TYPES = {
    int: NumArg,
    float: NumArg,
    str: TextArg,
    buffer: TextArg,
    unicode: TextArg,
    dict: JSONArg,
    bool: BooleanArg,
    list: ArrayArg,
    tuple: ArrayArg
}


def api_compiler(schema, action, params=None):
    """Compiles an WSGI request data into SQL text.

    Args:
        schema: Postgresql Schema namespace (str).
        action: Postgresql UDF/View name (str).
        params: Array of parameters - UDF's only (list/tuple/set/container).

    Returns:
        Postgresql executable SQL text (str).

    Examples:
        >>> api_compiler('cms', 'migrate', [1, ['a', 'b', 'c'], True])
        "SELECT * FROM cms.migrate(1, '{a, b, c}', TRUE)"
        >>> api_compiler('cms', 'log_view')
        'SELECT * FROM cms.log_view'
    """

    sql_cmp = 'SELECT * FROM {schema}.{action}'.format(
        schema=schema,
        action=action
    )

    if not params:
        return sql_cmp

    db_params = [FUNC_TYPES[type(val)](val).validate() for val in params]

    return sql_cmp + '({db_params})'.format(db_params=', '.join(db_params))


class PGPlugin(object):
    """Bottle.py Postgresql DB connection plugin (for Plugin.API v2)
     
    Attributes:
        api (int): The plugin API version for `bottle.py`
        name (str): The default name of the plugin keyword.
    """
    name = 'db'

    api = 2

    def __init__(self, keyword='db', **conn_data):
        self.keyword = keyword
        self._conn_data = conn_data
        self._conn = None
        self._api_view = None

    @property
    def connection(self):
        if not self._conn or self._conn.closed == 1:
            self._conn = psycopg2.connect(**self._conn_data)
            self._conn.autocommit = True
        return self._conn

    @property
    def version(self):
        with self.connection.cursor() as c:
            c.execute('select version();')
            data = c.fetchone()[0]
        self.connection.commit()
        return data

    @property
    def api_view(self):

        with self.connection.cursor(cursor_factory=RealDictCursor) as c:
            with open(SQL_DIR + '/dbapi.sql', 'r') as sql_file:
                sql_raw = sql_file.read()
            c.execute(sql_raw)
            api = c.fetchall()

        self.connection.commit()

        return api

    def setup(self, app):
        """ Make sure that other installed plugins don't affect the same
            keyword argument and check if metadata is available.
        """
        for other in app.plugins:
            if not isinstance(other, PGPlugin):
                continue
            if other.keyword == self.keyword:
                raise bottle.PluginError("Found another db plugin "
                                         "with conflicting settings ("
                                         "non-unique keyword).")

    def apply(self, callback, context):
        fn_args = inspect.getargspec(context.callback)[0]

        if self.keyword not in fn_args:
            return callback

        def wrapper(*args, **kwargs):
            kwargs[self.keyword] = self
            return callback(*args, **kwargs)

        return wrapper

if __name__ == '__main__':
    import doctest
    doctest.testmod()
