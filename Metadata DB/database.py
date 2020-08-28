import pymysql
import mysql.connector


def escape_strings(string):
    string = pymysql.escape_string(string)
    return string


def database_connection():
    """
    Create an object used to open and manage a connection to a MySQL server,
    send command and SQL statements and read the results.
    """

    db_connection = mysql.connector.connect(
        host="IP_ADDRESS",
        user="USER",
        passwd="PASSWORD",
        database="DB_NAME",
        charset='utf8',
        use_unicode=True)
    db_cursor = db_connection.cursor()
    db_cursor.execute("SET @@global.sql_mode= ''")
    return db_connection, db_cursor


def metadata_to_db(meta: dict, table: str):
    """
    Connects to the database and write the metadata stored in meta
    as a row in the table passed as string argument.
    It automatically adds new columns if needed.
    """
    db_connection, db_cursor = database_connection()
    db_cursor.execute("DESC TABLE_NAME")
    columns = [x[0] for x in db_cursor.fetchall()]
    for k, v in meta.items():
        key = escape_strings(k)
        value = escape_strings(v)
        meta[key] = value
    for key in meta.keys():
        if key not in columns:
            db_cursor.execute("ALTER TABLE {} ADD {} VARCHAR(255)".format(table,
                                                                          key))

    sql = "INSERT INTO (%s) (%s) VALUES ('%s')" % (table,
                                                   ", ".join(meta.keys()),
                                                   "', '".join(meta.values()))
    db_cursor.execute(sql)
    db_connection.commit()
    return
