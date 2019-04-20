import mysql.connector as connector
import Pass as pws
import twitter
import json
from datetime import datetime
import unicodedata
from unidecode import unidecode
import time

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


def demojify(in_str):
    re_str = ""

    for character in in_str:
        try:
            character.encode("ascii")
            re_str += character
        except UnicodeEncodeError:
            re_str += " "

    return re_str


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
time.sleep(2)
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

unaccessable_timelines = []
for user in memberList:
    try:
        timeline = twitter_API.GetUserTimeline(
            user_id = user.id,
            trim_user = True,
            include_rts = False
        )
    except:
        unaccessable_timelines.append(user.screen_name)
        continue # if for some reason not allowed to read timeline, go to next user

    time.sleep(10)
    for tweet in timeline:
        creation_date = datetime.strptime(tweet.created_at, "%a %b %d %H:%M:%S %z %Y")
        tweet_text = demojify(tweet.full_text).replace("'", "").replace("\"", "").replace(",", "")
        # print(json.dumps(json.loads(str(tweet)), indent = 3, sort_keys = False))

        # Insert the tweet into the database.
        print("Insert: " + tweet.full_text + "\n")
        db_cursor.execute(
            "INSERT INTO tweet (twitter_tweet_id, twitter_user_id, full_text, favorites_count, retweet_count, creation_date, creation_time," +
            "lang, device, uses_media) VALUES ({0}, {1}, '{2}', {3}, {4}, '{5}', '{6}', '{7}', '{8}', b'{9}');".format(
                tweet.id,
                user.id,
                tweet_text[:400] if len(tweet_text) > 400 else tweet_text,
                tweet.favorite_count, 
                tweet.retweet_count,
                creation_date.strftime("%Y-%m-%d"),
                creation_date.strftime("%H:%M:%S"),
                tweet.lang,
                tweet.source,
                str(1) if hasattr(user, "media") else str(0)
            )
        )
        # Insert the used hashtags into the database.
        for tag in tweet.hashtags:
            db_cursor.execute(
                "INSERT INTO tweet_hashtag (twitter_tweet_id, hashtag_str) VALUES ({0}, '{1}');".format(
                    str(tweet.id),
                    tag.text
                )
            )
        # Insert all the mentioned users into the database.
        for mentioned_user in tweet.user_mentions:
            db_cursor.execute(
                "INSERT INTO tweet_mentioned_user (twitter_tweet_id, mentioned_user_id) VALUES ({0}, {1});".format(
                    tweet.id,
                    mentioned_user.id
                )
            )

        db.commit()
    
    


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

print("Could not access following timelines:")
for name in unaccessable_timelines:
    print(name)
db.close()
