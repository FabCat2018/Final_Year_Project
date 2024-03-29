import pyodbc

_conn = pyodbc.connect("Driver={SQL Server};Server=tcp:DESKTOP-U3ATH6F,1433;Database=Final Year Project;Trusted_Connection=yes;")


class DatabaseConnector:

    # Setup DB connection
    @staticmethod
    def setup_db_connection():
        cursor = _conn.cursor()
        return cursor

    # Close DB connection
    @staticmethod
    def close_db_connection():
        _conn.close()
