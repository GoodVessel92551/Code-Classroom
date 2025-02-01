from dotenv import load_dotenv
from pymongo import MongoClient
import os
from flask import Flask, render_template, request, jsonify,redirect,session
import requests ,json
from oauthlib.oauth2 import WebApplicationClient
from datetime import timedelta 

load_dotenv(override=True, interpolate=False)

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

def login():
    if session.get("token"):
        keys = global_data_db.find_one({"name":"B-KEYS"})
        if str(hash_value(session.get("token"))) in keys["data"]:
            return True
    return False

def gen_user_token():
    chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    token = ""
    for i in range(20):
        token += random.choice(chars)
    return token


def create_account_google(username,id):
    ids = global_data_db.find_one({"name":"usernames"})["data"]
    if str(id) in ids:
        pass
    else:
        user_data = {"username":username,"id":id,"type":"google","data":{}}
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
    

client = MongoClient(os.getenv('mongo_url'))
db = client["Booogle_Revise"]
global_data_db = db["Code_Global"]
user_data_db = db["Code_User"]
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", None)
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", None)
GOOGLE_DISCOVERY_URL = (
    "https://accounts.google.com/.well-known/openid-configuration"
)

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=365)

client = WebApplicationClient(GOOGLE_CLIENT_ID)

def get_google_provider_cfg():
    return requests.get(GOOGLE_DISCOVERY_URL).json()

@app.route("/")
def home():
    return "Test"

# @app.route("/")
# def home():
#     if fun.login():
#         return render_template("index.html",username=fun.get_username(),page="home")
#     return render_template("landing_page.html")

@app.route("/notifications")
def notifications():
    if login():
        return render_template("notifications.html",username=get_username(),page="notifications")
    return render_template("landing_page.html")

@app.route("/code")
def code():
    if login():
        return render_template("index.html",username=get_username(),page="quick code")
    return render_template("landing_page.html")

@app.route("/call")
def call():
    google_provider_cfg = get_google_provider_cfg()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]
    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri="https://code.booogle.app/login/callback",
        scope=["openid", "email", "profile"],
    )
    return redirect(request_uri)

@app.route("/login/callback",methods=["POST","GET"])
def callback():
    code = request.args.get("code")
    google_provider_cfg = get_google_provider_cfg()
    token_endpoint = google_provider_cfg["token_endpoint"]
    https_authorization_url = request.url.replace("http://","https://")
    token_url, headers, body = client.prepare_token_request(
        token_endpoint,
        authorization_response=https_authorization_url,
        redirect_url=request.base_url.replace("http://","https://"),
        code=code
    )
    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET),
    )

    # Parse the tokens!
    client.parse_request_body_response(json.dumps(token_response.json()))
    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    uri, headers, body = client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)
    if userinfo_response.json().get("email_verified"):
        unique_id = userinfo_response.json()["sub"]
        users_email = userinfo_response.json()["email"]
        picture = userinfo_response.json()["picture"]
        users_name = userinfo_response.json()["given_name"]
    else:
        return "User email not available or not verified by Google.", 400
    create_account_google(users_name,unique_id)
    return redirect("/")





app.run(host="0.0.0.0",port=5000,debug=True) 






