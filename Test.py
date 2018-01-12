from pymongo import MongoClient
import random
import string
import smtplib

from email.mime.text import MIMEText



client = MongoClient(host="127.0.0.1")


db = client.event_scrape


def api_key_gen():
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(32))




def add_user(firstName, lastName, email, db):

    userInfo = db.event_users.find_one({"email": email})

    if userInfo is None:
        userInfo = {}
        userInfo["firstName"] = firstName
        userInfo["lastName"] = lastName
        userInfo["email"] = email
        userInfo["apiKey"] = api_key_gen()

        db.event_users.insert(userInfo)

    return userInfo["apiKey"]

def send_api_key(apiKey, db):
    userInfo = locate_user(apiKey, db)
    fromaddr = 'project2422@gmail.com'
    toaddrs = userInfo["email"]
    msg = MIMEText("Here is the api key: "+apiKey)
    msg['Subject'] = "API Key for accessing event data repository"
    username = 'project2422@gmail.com'
    password = 'workingwell'
    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    # server.ehlo()
    # server.starttls()
    server.login(username, password)
    server.sendmail(fromaddr, toaddrs, msg.as_string())
    server.quit()

def locate_user(apiKey, db):
    return db.event_users.find_one({"apiKey": apiKey})
""








