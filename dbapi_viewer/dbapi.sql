SELECT
    n.nspname AS api_namespace,
    'view'::text as api_type,
    c.relname AS api_name,
    'null'::json as api_params,
    '/' || n.nspname || '/' || c.relname || '/' api_endpoint
FROM pg_catalog.pg_class c LEFT JOIN pg_catalog.pg_namespace n
    ON (n.oid = c.relnamespace)
WHERE
    c.relkind  = 'v' and
    n.nspname not in ('public', 'tiger', 'pg_catalog', 'topology', 'information_schema')

union all

SELECT
    nspname api_namespace,
    'UDF'::text as api_type,
    proname api_name,
    to_json(proargnames) api_params,
    '/' || n.nspname || '/' || proname || '/' api_endpoint
FROM pg_catalog.pg_namespace n JOIN pg_catalog.pg_proc p
    ON pronamespace = n.oid
WHERE nspname not in ('public', 'tiger', 'pg_catalog', 'topology', 'information_schema')

order by api_namespace desc;