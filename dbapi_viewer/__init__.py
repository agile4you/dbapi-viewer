# -*- coding: utf-8 -*-
"""`dbapi_viewer` package.


Provides an easy-to-use HTTP API abstraction layer for
inspecting 

GET /search/entities?term={"name": "pav", "age": [1, 2, 3, 4]}


Process:
    -> Execute query `select * from search.entities('pav', '{1, 2, 3, 4}')
    -> Return a JSON Body {"resp_rows": "multiple", "api_data": []..}, query data.
"""


