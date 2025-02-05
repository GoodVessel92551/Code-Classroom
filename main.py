from dotenv import load_dotenv
from pymongo import MongoClient
import os
from flask import Flask, render_template, request, jsonify,redirect,session
import requests ,json
from oauthlib.oauth2 import WebApplicationClient
import fun
from datetime import timedelta 

load_dotenv(override=True, interpolate=False)

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

public_classes_placeholders = [
    {"classInfo":{"name":"Classname","description":"Lorem ipsum dolor sit amet consectetur. Auctor metus dui ullamcorper sed nunc id venenatis.","coverImage":"red","status":"Verified"}},
    {"classInfo":{"name":"Classname","description":"Lorem ipsum dolor sit amet consectetur. Auctor metus dui ullamcorper sed nunc id venenatis.","coverImage":"green","status":"Verified"}},
    {"classInfo":{"name":"Classname","description":"Lorem ipsum dolor sit amet consectetur. Auctor metus dui ullamcorper sed nunc id venenatis.","coverImage":"pink","status":"Verified"}},
    {"classInfo":{"name":"Classname","description":"Lorem ipsum dolor sit amet consectetur. Auctor metus dui ullamcorper sed nunc id venenatis.","coverImage":"blue","status":"Verified"}}
]

def get_google_provider_cfg():
    return requests.get(GOOGLE_DISCOVERY_URL).json()

@app.route("/")
def home():
    if fun.login():
        return render_template("index.html",username=fun.get_username(),page="home")
    return render_template("landing_page.html",publicClasses=public_classes_placeholders)

@app.route("/notifications")
def notifications():
    if fun.login():
        return render_template("notifications.html",username=fun.get_username(),page="notifications")
    return render_template("landing_page.html",publicClasses=public_classes_placeholders)

@app.route("/code")
def code():
    if fun.login():
        return render_template("code.html",username=fun.get_username(),page="quick code")
    return render_template("landing_page.html")

@app.route("/call")
def call():
    host = request.host
    subdomain = host.split('.')[0]
    if subdomain == "devcode":
        redirect_url = "https://devcode.booogle.app/login/callback"
    elif subdomain == "code-dev":
        redirect_url = "https://code_dev.booogle.app/login/callback"
    else:
        redirect_url = "https://code.booogle.app/login/callback"
    google_provider_cfg = get_google_provider_cfg()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]
    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=redirect_url,
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
    fun.create_account_google(users_name,unique_id)
    return redirect("/")





if __name__ == "__main__":
    app.run(debug=True)






