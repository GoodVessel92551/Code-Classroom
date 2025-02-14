import hashlib
import random
from flask import session
from dotenv import load_dotenv
from pymongo import MongoClient
import os

client = MongoClient(os.getenv('mongo_url'))
db = client["Booogle_Revise"]
global_data_db = db["Code_Global"]
user_data_db = db["Code_User"]

def hash_value(data):
    """
    Calculates the SHA-256 hash value of the given data.

    Args:
        data: The data to be hashed.

    Returns:
        The SHA-256 hash value of the data as a hexadecimal string.
    """
    sha256 = hashlib.sha256()
    sha256.update(str(data).encode('utf-8'))
    return sha256.hexdigest()

def password_hash(password, salt=os.getenv("salt"), iterations=100000, dklen=64, hashfunc=hashlib.sha256):
    key = password.encode('utf-8')
    salt = salt.encode('utf-8')
    return hashlib.pbkdf2_hmac(hashfunc().name, key, salt, iterations, dklen)

def signup_user(username,password,confirmPassword):
    session.permanent = True
    if len(username) < 2:
        return "Username is too short"
    elif len(username) > 20:
        return "Username is too long"
    elif password != confirmPassword:
        return "Passwords do not match"
    
    id = gen_user_id()
    ids = global_data_db.find_one({"name":"usernames"})["data"]
    if str("UNAPW-"+username) in ids:
        return "Username already exists"
    else:
        user_data = {"username":username,"password":password,"id":id,"type":"UNAPW","data":{"aiTools":{"weakTopics":{"topics":[],"tasks":[]}}}}
        user_data_db.insert_one(user_data)
        query = {"name":"usernames"}
        update = {"$push":{"data":"UNAPW-"+username}}
        global_data_db.update_one(query, update)
    user_token = gen_user_token()
    session["token"] = user_token
    query = {"name":"B-KEYS"}
    update = {"$set":{f"data.{hash_value(user_token)}":{"type":"UNAPW","username":username}}}
    global_data_db.update_one(query, update)
    return "Success"

def login_user(username,password):
    session.permanent = True
    ids = global_data_db.find_one({"name":"usernames"})["data"]
    if str("UNAPW-"+username) in ids:
        user = user_data_db.find_one({"username":username})
        if user["password"] == password:
            user_token = gen_user_token()
            session["token"] = user_token
            query = {"name":"B-KEYS"}
            update = {"$set":{f"data.{hash_value(user_token)}":{"type":"UNAPW","username":username}}}
            global_data_db.update_one(query, update)
            return "Success"
        else:
            return "Incorrect Password"
    else:
        return "Username does not exist"

def gen_user_token():
    chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    token = ""
    for i in range(20):
        token += random.choice(chars)
    return token

def gen_user_id():
    chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    id = "G-"
    for i in range(15):
        id += random.choice(chars)
    return id

def login():
    if session.get("token"):
        keys = global_data_db.find_one({"name":"B-KEYS"})
        if str(hash_value(session.get("token"))) in keys["data"]:
            return True
    return False


def create_account_google(username,id):
    session.permanent = True
    ids = global_data_db.find_one({"name":"usernames"})["data"]
    if str(id) in ids:
        pass
    else:
        user_data = {"username":username,"id":id,"type":"google","data":{"aiTools":{"weakTopics":{"topics":[],"tasks":[]}}}}
        user_data_db.insert_one(user_data)
        query = {"name":"usernames"}
        update = {"$push":{"data":id}}
        global_data_db.update_one(query, update)
    user_token = gen_user_token()
    session["token"] = user_token
    query = {"name":"B-KEYS"}
    update = {"$set":{f"data.{hash_value(user_token)}":{"type":"Google","username":id}}}
    global_data_db.update_one(query, update)


def get_id():
    keys = global_data_db.find_one({"name":"B-KEYS"})
    token = hash_value(session.get("token"))
    type = keys["data"][token]["type"]
    username = keys["data"][token]["username"]
    if type == "UNAPW":        
        id = user_data_db.find_one({"username":username})["id"]
    else:
        id = username
    
    print(id)
    return id


def get_username():
    print(get_id())
    username = user_data_db.find_one({"id":str(get_id())})["username"]
    return username
    

def weak_topics(id,data):
    user_data = user_data_db.find_one({"id":id})
    topics = user_data["data"]["aiTools"]["weakTopics"]["topics"]
    topics.append(data)
    query = {"id":id}
    update = {"$set":{"data.aiTools.weakTopics.topics":topics}}
    user_data_db.update_one(query, update)
    return "Success"