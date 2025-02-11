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

def password_hash(password, salt, iterations=100000, dklen=64, hashfunc=hashlib.sha256):
    key = password.encode('utf-8')
    salt = salt.encode('utf-8')
    return hashlib.pbkdf2_hmac(hashfunc().name, key, salt, iterations, dklen)


def gen_user_token():
    chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    token = ""
    for i in range(20):
        token += random.choice(chars)
    return token


def login():
    if session.get("token"):
        keys = global_data_db.find_one({"name":"B-KEYS"})
        if str(hash_value(session.get("token"))) in keys["data"]:
            return True
    return False


def create_account_google(username,id):
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
    update = {"$set":{f"data.{hash_value(user_token)}":id}}
    global_data_db.update_one(query, update)


def get_id():
    keys = global_data_db.find_one({"name":"B-KEYS"})
    id = keys["data"][str(hash_value(session.get("token")))]
    return id


def get_username():
    print(get_id())
    username = user_data_db.find_one({"id":str(get_id())})["username"]
    return username
    