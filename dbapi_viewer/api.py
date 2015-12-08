# -*- coding: utf-8 -*-
"""'Base API spec.'

GET /search/entities?term={"name": "pav", "age": [1, 2, 3, 4]}


Process:
    -> Execute query `select * from search.entities('pav', '{1, 2, 3, 4}')
    -> Return a JSON Body {"resp_rows": "multiple", "api_data": []..}, data.
"""

__license__ = 'GLPv3'
__date__ = '13-11-2015'
__author__ = 'Papavassiliou Vassilis'
__version__ = '0.0.1'
__all__ = ['index_handler', 'main_handler']


import bottle
import pgtools
import psycopg2.extras
from simplejson import JSONDecodeError
from collections import OrderedDict


class InvalidParamsError(Exception):
    """Raises if http request params is invalid.
    """
    pass


def request_to_params(request_context, serializer_cls=pgtools.json):
    """Converts 'bottle.request' data to a list of values.

    Args:
        request_context: WSGI-request local-context instance.
        serializer_cls: JSON Serialization callable.

    Returns:

        A list of cleaned HTTP parameters.

    Raises:

        Invalid Input, if serialization fails.
    """

    raw_params = request_context

    if not raw_params:
        return []

    try:
        cleaned_params = serializer_cls.loads(
            raw_params,
            object_pairs_hook=OrderedDict
        )

        return cleaned_params.values()

    except JSONDecodeError:
        raise InvalidParamsError("Invalid Parameter format")


def index_handler(db):
    schema_data = db.api_view

    schema_root = {
        "namespaces_count": len(set([i['api_namespace'] for i in schema_data])),
        "schemas": sorted(list(set([i['api_namespace'] for i in schema_data]))),
        "namespaces": []
    }

    for schema in set([i['api_namespace'] for i in schema_data]):
        schema_views = [d for d in schema_data
                        if d['api_namespace'] == schema and
                        d['api_type'] == 'view']
        schema_udf = [d for d in schema_data
                        if d['api_namespace'] == schema and
                        d['api_type'] == 'UDF']
        schema_info = {
            "name": schema,
            "functions": [{'name': i['api_name'], 'uri': i['api_endpoint'],
                     'args': i['api_params']} for i in schema_udf],
            "views": [{'name': i['api_name'], 'uri': i['api_endpoint'],
                     'args': i['api_params']} for i in schema_views]
        }
        schema_root["namespaces"].append(schema_info)

    return bottle.jinja2_template('index.html', schema_root)


def main_handler(schema, action, db):
    """Main Service EntryPoint.

    Args:
        schema (str): Postgresql schema namespace.
        action (str): Postgresql UDF / View name.
        db (instance): A database instance.

    Returns:
        JSON response for a specified db api.
    """
    if bottle.request.method == 'GET':
        params = bottle.request.params.get('args')
    else:
        params = bottle.request.body.read()

    p = request_to_params(params)

    sql = pgtools.api_compiler(schema, action, p)

    with db.connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)\
            as c:
        try:
            c.execute(sql)
            resp_data = c.fetchall()
        except psycopg2.Error, e:
            return {"DBError": e.args}

    return {"Query Execution": sql,
            "results": resp_data}
