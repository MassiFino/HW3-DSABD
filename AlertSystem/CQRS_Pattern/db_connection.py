import mysql.connector
import mysql.connector.errors
import os

mysql_host = os.getenv('DATABASE_HOST', 'mysql-service')
mysql_user = os.getenv('DATABASE_USER', 'root')
mysql_password = os.getenv('DATABASE_PASSWORD', '1234')
mysql_db = os.getenv('DATABASE_NAME', 'yfinance_db')
mysql_port = int(os.getenv('DATABASE_PORT', '3306'))

# Crea il dizionario di configurazione includendo la porta
db_config = {
    'host': mysql_host,
    'port': mysql_port,  # Includi la porta
    'user': mysql_user,
    'password': mysql_password,
    'database': mysql_db
}

def get_db_connection():
    try:
        connection = mysql.connector.connect(**db_config)
        if connection.is_connected():
            return connection
    except mysql.connector.Error as err:
        print(f"Errore durante la connessione al database: {err}")
    return None