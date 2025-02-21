from dotenv import load_dotenv
from pymongo import MongoClient
import os
from flask import Flask, render_template, request, jsonify,redirect,session,url_for
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
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=30)

client = WebApplicationClient(GOOGLE_CLIENT_ID)

public_classes_placeholders = [
    {"id":"1","classInfo":{"name":"Classname","description":"Lorem ipsum dolor sit amet consectetur. Auctor metus dui ullamcorper sed nunc id venenatis.","coverImage":"red","status":"Verified"}},
    {"id":"2","classInfo":{"name":"Classname","description":"Lorem ipsum dolor sit amet consectetur. Auctor metus dui ullamcorper sed nunc id venenatis.","coverImage":"green","status":"Verified"}},
    {"id":"3","classInfo":{"name":"Classname","description":"Lorem ipsum dolor sit amet consectetur. Auctor metus dui ullamcorper sed nunc id venenatis.","coverImage":"pink","status":"Verified"}},
    {"id":"4","classInfo":{"name":"Classname","description":"Lorem ipsum dolor sit amet consectetur. Auctor metus dui ullamcorper sed nunc id venenatis.","coverImage":"blue","status":"Verified"}} 
]

classes_placeholders = {
    "huwser89":{"classInfo":{"id":"huwser89","name":"Maths","description":"Lorem ipsum dolor sit amet consectetur. Auctor metus dui ullamcorper sed nunc id venenatis.","classSubTitle":"Maths Class","coverImage":"red"},"messages":[{"user":"John Doe","message":"Hello World","time":"12/02/25"},{"user":"John Doe","message":"Hello World","time":"12/02/25"},{"user":"John Doe","message":"Hello World","time":"12/02/25"}],"tasks":[{"id":"uiohsedrfg","taskName":"Task Name","taskDescription":"Lorem ipsum dolor sit amet consectetur. Auctor metus dui ullamcorper sed nunc id venenatis.","taskDue":"15/02/25","taskStatus":"completed"}]},
    "y78fsh":{"classInfo":{"id":"y78fsh","name":"Physics","description":"Lorem ipsum dolor sit amet consectetur. Auctor metus dui ullamcorper sed nunc id venenatis.","classSubTitle":"Physics Class","coverImage":"green"},"messages":[{"user":"John Doe","message":"Hello World","time":"12/02/25"},{"user":"John Doe","message":"Hello World","time":"12/02/25"},{"user":"John Doe","message":"Hello World","time":"12/02/25"}],"tasks":[{"id":"yuihggf","taskName":"Task Name","taskDescription":"Lorem ipsum dolor sit amet consectetur. Auctor metus dui ullamcorper sed nunc id venenatis.","taskDue":"15/02/25","taskStatus":"missing"}]},
    "huy8s9r":{"classInfo":{"id":"huy8s9r","name":"Computer Science","description":"Lorem ipsum dolor sit amet consectetur. Auctor metus dui ullamcorper sed nunc id venenatis.","classSubTitle":"Computer Science Class","coverImage":"blue"},"messages":[{"user":"John Doe","message":"Hello World","time":"12/02/25"},{"user":"John Doe","message":"Hello World","time":"12/02/25"},{"user":"John Doe","message":"Hello World","time":"12/02/25"}],"tasks":[{"id":"hbjsdfg","taskName":"Task Name","taskDescription":"Lorem ipsum dolor sit amet consectetur. Auctor metus dui ullamcorper sed nunc id venenatis.","taskDue":"15/02/25","taskStatus":"notcompleted"}]},
}

def get_google_provider_cfg():
    return requests.get(GOOGLE_DISCOVERY_URL).json()

@app.route("/")
def home():
    if fun.login():
        return render_template("index.html",username=fun.get_username(),page="home",classes=classes_placeholders)
    return render_template("landing_page.html",publicClasses=public_classes_placeholders)

@app.route("/faq")
def faq():
    return render_template("FAQ.html")

@app.route("/notifications")
def notifications():
    if fun.login():
        return render_template("notifications.html",username=fun.get_username(),page="notifications",classes=classes_placeholders)
    return render_template("landing_page.html",publicClasses=public_classes_placeholders)

@app.route("/code")
def code():
    if fun.login():
        return render_template("code.html",username=fun.get_username(),page="quick code",classes=classes_placeholders)
    return render_template("landing_page.html")

@app.route("/classroom/<classid>")
def class_page(classid):
    print(classid)
    if fun.login():
        user_class = classes_placeholders[classid]
        return render_template("class.html",username=fun.get_username(),page="class"+classid,classes=classes_placeholders,user_class=user_class)
    return render_template("landing_page.html")

@app.route("/task")
def task():
    if fun.login():
        return render_template("task.html",username=fun.get_username(),page="tasks",classes=classes_placeholders)
    return render_template("landing_page.html")



@app.route("/endpoint/ai/getweaktopics",methods=["GET"])
def get_weak_topics():
    if fun.login():
        userid = fun.get_id()
        print("User ID",userid)
        data = fun.get_weak_topics(userid)
        return jsonify(data)
    return "Not logged in"

@app.route("/endpoint/ai/weaktopics",methods=["POST"])
def weak_topics():
    if fun.login():
        userid = fun.get_id()
        print("User ID",userid)
        data = request.json
        data = data["result"]
        fun.weak_topics(userid,data)
    return "complete"

@app.route("/endpoint/auth/login",methods=["POST"])
def login_endpoint():
    session.permanent = True
    form_data = request.form
    username = form_data["username"]
    password = fun.password_hash(form_data["password"])
    error = fun.login_user(username,password)
    if error != "Success":
        return render_template("auth/login.html",error=error)
    return redirect("/")

@app.route("/endpoint/auth/signup",methods=["POST"])
def signup_endpoint():
    session.permanent = True
    form_data = request.form
    username = form_data["username"]
    if len(form_data["password"]) < 5:
        return "Password is too short"
    elif len(form_data["password"]) > 15:
        return "Password is too long"
    password = fun.password_hash(form_data["password"])
    confirmPassword = fun.password_hash(form_data["confirmPassword"])
    error = fun.signup_user(username,password,confirmPassword)
    if error != "Success":
        return render_template("auth/signup.html",error=error)
    return redirect("/")


@app.route("/login")
def login_page():
    return render_template("auth/login.html",error=False)

@app.route("/signup")
def signup_page():
    return render_template("auth/signup.html",error=False)

@app.route("/signout")
def signout():
    session.clear()
    return redirect("/")

@app.route("/call")
def call():
    session.permanent = True
    host = request.host
    subdomain = host.split('.')[0]
    if subdomain == "devcode":
        redirect_url = "https://devcode.booogle.app/login/callback"
    elif subdomain == "code-dev":
        redirect_url = "https://code-dev.booogle.app/login/callback"
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
    session.permanent = True
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


@app.errorhandler(404)
def page_not_found(error):
    if fun.login():
        return render_template('404.html', username=fun.get_username(), classes=classes_placeholders,page="404"), 404
    return render_template('404.html'), 404


if __name__ == "__main__":
    app.run(debug=True)






