import mysql.connector as connector
import Pass as pws
import twitter

# Connect to database.
db = connector.connect(
    host = "localhost",
    user = pws.DB_USERNAME,
    passwd = pws.DB_PASSWORD,
    auth_plugin = "mysql_native_password",
    database = "db_synchro"
)
db_cursor = db.cursor()

# Connect to Twitter.
twitter_API = twitter.Api(
    consumer_key = pws.CONS_KEY,
    consumer_secret = pws.CONS_SECRET,
    access_token_key = pws.ACC_TOKEN,
    access_token_secret = pws.ACC_SECRET
)
print("\n" + str(twitter_API.VerifyCredentials()) + "\n")

print(twitter_API.GetListMembers(
    slug = "politik_bundestag_mdb_all",
    owner_id = twitter_API.GetUser(screen_name = "christoph_z").id
))



db_cursor.execute("SELECT * FROM pic_info;")
result = db_cursor.fetchall()
print(db_cursor.rowcount)

for row in result:
    print(row[0] + "\n" + row[3])
    print("\n")

print(db_cursor)

# Idee: Metadaten über User in R analysieren
