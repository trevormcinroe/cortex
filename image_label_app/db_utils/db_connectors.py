import sqlite3
from passlib.hash import bcrypt

def user_query(db_name, usr, pswd):
    """

    Args:
        db_name:
        usr:
        pswd:

    Returns:
        username - str, password verification - bool

    """

    # Making a connection to the database
    # If it does not yet exist, SQLite will create it
    con = sqlite3.connect(database=db_name)

    # Creating our cursor object and then using it to execute the creation of the table
    cursor = con.cursor()

    # Querying the database and then using the fetchall() method to return the data
    cursor.execute("""SELECT username, password, name FROM users WHERE username=?""",
                   (usr,))
    result = cursor.fetchall()

    # Catch for when nothing is returned
    if len(result) == 0:
        return False, False, False

    # If a user was successfully returned, we need to make sure that the password matches
    # Thankfully, bcrypt has a nice convenience function that returns a BOOL
    return result[0][0], bcrypt.verify(pswd, result[0][1])


def increment_user_count(db_name, usr, increment=1):
    """

    Args:
        db_name:
        usr:
        increment:

    Returns:

    """
    # Making a connection to the database
    # If it does not yet exist, SQLite will create it
    con = sqlite3.connect(database=db_name)

    # Creating our cursor object which manages our connection to the db
    cursor = con.cursor()

    # Querying the database and then using the fetchall() method to return the data
    # The data returns as a list of tuples [(count,)]
    cursor.execute("""SELECT count FROM users WHERE username=?""",
                   (usr,))
    result = cursor.fetchall()[0][0]

    # Now adding our increment to the result
    new_count = result + increment

    # Updating the count value using our cursor
    # It is necessary to explicitly commit() our changes
    cursor.execute("""UPDATE users SET count=? where username=?""",
                   (new_count, usr,))
    con.commit()
    cursor.close()
