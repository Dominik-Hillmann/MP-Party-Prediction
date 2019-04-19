import mysql.connector as connector
import Pass as pws
import twitter
import json
from datetime import datetime

def get_party_label(user, api):
    s = user.description.lower()

    if ("spd" in s) or ("sozialdemokrat" in s):
        return "S"
    elif ("fdp" in s) or ("freie" in s):
        return "F"
    elif ("cdu" in s) or ("csu" in s) or ("christdemokrat" in s):
        return "C"
    elif ("linke" in s) or ("links" in s):
        return "L"
    elif ("grün" in s) or ("gruen" in s):
        return "G"
    elif ("afd" in s):
        return "A"
    else:
        timeline = api.GetUserTimeline(
            user_id = user.id,
            trim_user = True,
            include_rts = False
        )
        
        print("\n\nKeine automatische Zuordnung möglich für " + user.screen_name)
        print("Beschreibung: " + user.description + "\n")
        for i in range(3):
            try:
                text = timeline[i].full_text
            except:
                break

            print("Tweet " + str(i) + ": " + text + "\n")   

        print("Bitte Zuordnung treffen: ")
        re = input()
        return re.upper()


# Connect to database.
db = connector.connect(
    host = "localhost",
    user = pws.DB_USERNAME,
    passwd = pws.DB_PASSWORD,
    auth_plugin = "mysql_native_password"
)

db_cursor = db.cursor()

# Connect to Twitter.
twitter_API = twitter.Api(
    consumer_key = pws.CONS_KEY,
    consumer_secret = pws.CONS_SECRET,
    access_token_key = pws.ACC_TOKEN,
    access_token_secret = pws.ACC_SECRET,
    tweet_mode = "extended"
)

# Init of database, if it does not already exist.
for line in open("./Database_Init_4_Machine.sql"):
    db_cursor.execute(line)

# Get all the party members from this specific list: https://twitter.com/christoph_z/lists/politik-bundestag-mdb-all/members?lang=de
memberList = twitter_API.GetListMembersPaged(
    slug = "politik-bundestag-mdb-all",
    owner_id = twitter_API.GetUser(screen_name = "christoph_z").id,
    count = 498 # get all members in this list
)[2]
# print(json.dumps(json.loads(str(memberList[69])), indent = 3, sort_keys = False))

for user in memberList:
    db_cursor.execute("SELECT * from user WHERE user.twitter_user_id = '" + str(user.id) + "';")

    if len(db_cursor.fetchall()) == 0:
        creation_date = datetime.strptime(user.created_at, "%a %b %d %H:%M:%S %z %Y")

        try:
            db_cursor.execute(
                "INSERT INTO user (twitter_user_id, screen_name, favorites_count, followers_count, friends_count, listed_count, statuses_count," +
                "creation_date, creation_time, loc, link_color, sidebar_border_color, sidebar_fill_color, text_color, party) VALUES " + 
                "({0}, '{1}', {2}, {3}, {4}, {5}, {6}, '{7}', '{8}', '{9}', '{10}', '{11}', '{12}', '{13}', '{14}');".format(
                    user.id,
                    user.screen_name,
                    user.favourites_count,
                    user.followers_count,
                    user.friends_count,
                    user.listed_count,
                    user.statuses_count,
                    creation_date.strftime("%Y-%m-%d"),
                    creation_date.strftime("%H:%M:%S"),
                    user.location.replace(",", ""),
                    user.profile_link_color,
                    user.profile_sidebar_border_color,
                    user.profile_sidebar_fill_color,
                    user.profile_text_color,
                    get_party_label(user, twitter_API)
                )
            )
            db.commit()
            
        except:
            print("Fehler: versuche nächstes Listenmitglied...")
            continue
    
    


# timeline = twitter_API.GetUserTimeline(
#     user_id = memberList[69].id,
#     trim_user = True, # only return tweet, not associated user data
#     include_rts = False # no retweets
# )

# print(
#     json.dumps(json.loads(str(memberList[69])), indent = 3, sort_keys = False)
# )

# for tweet in timeline:
#     print(
#         json.dumps(json.loads(str(tweet)), indent = 3, sort_keys = False)
#     )
#     print("\n")

# for member in memberList:
#     print(member.screen_name + "\n")






# db_cursor.execute("SELECT * FROM pic_info;")
# result = db_cursor.fetchall()
# # print(db_cursor.rowcount)

# for row in result:
#     print(row[0] + "\n" + row[3])
#     print("\n")

# print(db_cursor)

# Idee: Metadaten über User in R analysieren

# User-Schema in der Datenbank: was soll es enthalten:
    # creation_day, creation_month, creation_year, creation_hour, creation_min
    # favorites_count, followers_count, friends_count, listed_count
    # KEY: id
    # lang, location -> auf Koords mappen? Konzentrieren sich Abgeordnete geographisch?
    # link_color, sidebar_border_color, sidebar_fill_color, text_color
    # screen_name

# Tweet-Schema:
    # KEY: tweet_id
    # user_id
    # full_text
    # creation_day, creation_month, creation_year, creation_hour, creation_min
    # lang
    # bool: uses_media
    # retweet_count, favorite_count
    # hashtags (zusammen als String, getrennt durch Kommas)
    # device (== source)

# n-n-Beziehungen: eigene Relationen
    # Tweet-Hashtag-Schema:
        # tweet_id
        # hashtag_str
    # Tweet_Mentioned_User-Schema:
        # tweet_id
        # user_id

db.close()
