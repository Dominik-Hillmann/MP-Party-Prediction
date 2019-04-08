import mysql.connector as connector
import Pass as db_data

db = connector.connect(
    host = "localhost",
    user = db_data.DB_USERNAME,
    passwd = db_data.DB_PASSWORD,
    auth_plugin = "mysql_native_password",
    database = "db_synchro"
)

db_cursor = db.cursor()
db_cursor.execute("SELECT * FROM pic_info;")
result = db_cursor.fetchall()
print(db_cursor.rowcount)

for row in result:
    print(row[0] + "\n" + row[3])
    print("\n")
