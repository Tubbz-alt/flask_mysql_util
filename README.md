This is a small utility for using MySQL from within Flask.

It attaches `before_request` and `teardown_request` hooks to create and close connections to the specified database.
In addition, it initializes the connection using environment variables.

#### Basic Usage.
In your Flask context object create a database connection  
`logbook_db = MultiMySQL(prefix="LOGBOOK")`

The prefix you use for the database must be unique in your application.
It is also used to look up the database connection properties in the application environment.
For example, in this case, the following environment variables will be used to connect to the database.
- LOGBOOK_DATABASE_HOST
- LOGBOOK_DATABASE_DB
- LOGBOOK_DATABASE_USER
- LOGBOOK_DATABASE_PASSWORD
- LOGBOOK_DATABASE_CHARSET
- LOGBOOK_DATABASE_USE_UNICODE


In your Flask app initialization, (for example, `start.py`), initialize the connection using the `app`.
The environment variables from the environment are used to initialize the connection during the `init_app` call.

```
from context import logbook_db

logbook_db.init_app(app)
```

Use the connection in your business object.
```
from context import logbook_db

with logbook_db.connect() as cursor:
  cursor.execute(QUERY_SELECT_EXPERIMENTS_FOR_INSTRUMENT)
  return { row['experiment_id'] : row for row in  cursor.fetchall() }
```
