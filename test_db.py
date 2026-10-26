
import oracledb
from getpass import getpass

username = input("Oracle username: ")
password = getpass("Oracle password: ")
service = input("Oracle service name: ")

try:
    connection = oracledb.connect(
        user=username,
        password=password,
        host="localhost",
        port=1521,
        service_name=service
    )

    print("SUCCESS: Oracle connection established!")

    cursor = connection.cursor()
    cursor.execute("SELECT USER FROM dual")
    print("Connected database user:", cursor.fetchone()[0])

    cursor.close()
    connection.close()

except oracledb.Error as error:
    print("Connection failed:", error)
