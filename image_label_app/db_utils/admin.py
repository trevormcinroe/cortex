import sqlite3
from passlib.hash import bcrypt

def create_user_db(db_name):
    """

    Args:
        db_name:

    Returns:

    """

    # Making a connection to the database
    # If it does not yet exist, SQLite will create it
    con = sqlite3.connect(database=db_name)

    # Creating our cursor object and then using it to execute the creation of the table
    cursor = con.cursor()
    cursor.execute("""
        CREATE TABLE users(id INTEGER PRIMARY KEY,
                            username TEXT,
                            password TEXT,
                            name TEXT,
                            count INTEGER
        )""")

    # Committing and then closing the connection. Because, best practices and stuff
    con.commit()
    cursor.close()

def create_user(db_name, usr, pswd, name, count=0):
    """

    Args:
        db_name:
        usr:
        pswd:
        name:

    Returns:

    """

    # Making a connection to the database
    # If it does not yet exist, SQLite will create it
    con = sqlite3.connect(database=db_name)

    # Creating our cursor object and then using it to execute the creation of the table
    cursor = con.cursor()
    cursor.execute("""INSERT INTO users(username, password, name, count) VALUES(?, ?, ?, ?)""",
                   (usr, bcrypt.hash(pswd), name, count))

    # You already know
    con.commit()
    cursor.close()


def query_db(db_name):
    """

    Args:
        db_name:

    Returns:

    """

    # Making a connection to the database
    # If it does not yet exist, SQLite will create it
    con = sqlite3.connect(database=db_name)

    # Creating our cursor object and then using it to execute the creation of the table
    cursor = con.cursor()
    cursor.execute("""SELECT * FROM users""")

    return cursor.fetchall()

print(query_db(db_name='core'))
# create_user_db(db_name='core')
# create_user(db_name='core',
#             usr='trevor_mcinroe@quadraticinsights.com',
#             pswd='bigballs69',
#             name='trevor')