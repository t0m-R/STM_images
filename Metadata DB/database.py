import pymysql
import mysql.connector

def EscapeStrings(stmstring):
    escape_strings = pymysql.escape_string(stmstring)
    return escape_strings

def DatabaseConnection():
        db_connection=mysql.connector.connect(
                host= "IP_ADDR",
                user= "USER",
                passwd= "PASSWORD",
                database="DB_NAME",
                charset='utf8',
                use_unicode=True)
        db_cursor = db_connection.cursor()
        db_cursor.execute("SET @@global.sql_mode= ''")
        return db_connection, db_cursor

def meta2db(meta, table):
    db_connection, db_cursor = DatabaseConnection()
    db_cursor.execute("DESC TABLE_NAME")
    columns = [x[0] for x in db_cursor.fetchall()]
    for k,v in meta.items():
        key = EscapeStrings(k)
        value = EscapeStrings(v)
        meta[key] = value
    for key in meta.keys():
        if key not in columns:
            db_cursor.execute("ALTER TABLE {} ADD {} VARCHAR(255)".format(table,
                                                                          key))

    sql = "INSERT INTO TABLE_NAME (%s) VALUES ('%s')" %
            (", ".join(meta.keys()), "', '".join(meta.values()))
    db_cursor.execute(sql)
    db_connection.commit()
    return
