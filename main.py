from dotenv import load_dotenv
from pymongo import MongoClient
import os
from flask import Flask, render_template, request, jsonify,redirect,session,url_for
import requests ,json
from datetime import datetime
from oauthlib.oauth2 import WebApplicationClient
import fun
from datetime import timedelta 
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, Email, EqualTo
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_limiter.errors import RateLimitExceeded
import json

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
app.config['SESSION_COOKIE_HTTPONLY'] = True 
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

client = WebApplicationClient(GOOGLE_CLIENT_ID)

limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["1500 per day", "100 per hour"],
    storage_uri="memory://"
)

public_classes_placeholders = [
    {"id":"1","classInfo":{"name":"Classname","description":"Lorem ipsum dolor sit amet consectetur. Auctor metus dui ullamcorper sed nunc id venenatis.","coverImage":"red","status":"Verified"}},
    {"id":"2","classInfo":{"name":"Classname","description":"Lorem ipsum dolor sit amet consectetur. Auctor metus dui ullamcorper sed nunc id venenatis.","coverImage":"green","status":"Verified"}},
    {"id":"3","classInfo":{"name":"Classname","description":"Lorem ipsum dolor sit amet consectetur. Auctor metus dui ullamcorper sed nunc id venenatis.","coverImage":"pink","status":"Verified"}},
    {"id":"4","classInfo":{"name":"Classname","description":"Lorem ipsum dolor sit amet consectetur. Auctor metus dui ullamcorper sed nunc id venenatis.","coverImage":"blue","status":"Verified"}} 
]

class signupForm(FlaskForm):
    username = StringField('Username',validators=[DataRequired(),Length(min=2,max=20)],render_kw={"placeholder": "Username"})
    password = PasswordField('Password',validators=[DataRequired(),Length(min=5,max=15)],render_kw={"placeholder": "Password"})
    confirmPassword = PasswordField('Confirm Password',validators=[DataRequired(),EqualTo('password')],render_kw={"placeholder": "Confirm Password"})
    submit = SubmitField('Sign Up')

class loginForm(FlaskForm):
    username = StringField('Username',validators=[DataRequired(),Length(min=2,max=20)],render_kw={"placeholder": "Username"})
    password = PasswordField('Password',validators=[DataRequired(),Length(min=5,max=15)],render_kw={"placeholder": "Password"})
    submit = SubmitField('Login')


def get_google_provider_cfg():
    return requests.get(GOOGLE_DISCOVERY_URL).json()

@app.route("/")
def home():
    if fun.login():
        return render_template("index.html",username=fun.get_username(),userID=fun.get_user_id(),settings=fun.get_users_settings(),streak=fun.get_user_streak(),xp=fun.get_user_xp(),notifications=fun.get_notifications(),page="home",classes=fun.get_user_classes())
    return render_template("landing_page.html",publicClasses=public_classes_placeholders)

@app.route("/faq")
def faq():
    return render_template("FAQ.html")

@app.route("/privacyPolicy")
def privacy_policy():
    return render_template("Privacy Policy.html")

@app.route("/enableAI")
def enableAI():
    return render_template("enableAI.html")

@app.route("/notifications")
def notifications():
    if fun.login():
        return render_template("notifications.html",username=fun.get_username(),userID=fun.get_user_id(),settings=fun.get_users_settings(),streak=fun.get_user_streak(),xp=fun.get_user_xp(),notifications=fun.get_notifications(),page="notifications",classes=fun.get_user_classes())
    return redirect("/")

@app.route("/quickCode")
def code_project():
    if fun.login():
        fun.update_streak()
        return render_template("code.html",username=fun.get_username(),userID=fun.get_user_id(),settings=fun.get_users_settings(),streak=fun.get_user_streak(),xp=fun.get_user_xp(),notifications=fun.get_notifications(),page="quick code",classes=fun.get_user_classes())
    return redirect("/")

@app.route("/code")
def code():
    if fun.login():
        return render_template("quickCode.html",username=fun.get_username(),userID=fun.get_user_id(),settings=fun.get_users_settings(),streak=fun.get_user_streak(),xp=fun.get_user_xp(),notifications=fun.get_notifications(),page="quick code",classes=fun.get_user_classes())
    return redirect("/")

@app.route("/create/classroom")
def create_classroom():
    if fun.login():
        return render_template("create_class.html",username=fun.get_username(),userID=fun.get_user_id(),settings=fun.get_users_settings(),streak=fun.get_user_streak(),xp=fun.get_user_xp(),notifications=fun.get_notifications(),page="create classroom",classes=fun.get_user_classes())
    return redirect("/")

@app.route("/create/task/<classid>") 
def create_task(classid):
    if fun.login():
        if not fun.check_teacher(classid):
            return redirect("/classroom/"+classid)
        return render_template("create_task.html",username=fun.get_username(),userID=fun.get_user_id(),settings=fun.get_users_settings(),streak=fun.get_user_streak(),xp=fun.get_user_xp(),notifications=fun.get_notifications(),page="create task",classes=fun.get_user_classes(),classid=classid)
    return redirect("/")

@app.route("/classroom/<classid>")
def class_page(classid):
    print(classid)
    if fun.login():
        user_class = fun.get_class_with_users_tasks(classid)
        if user_class == None:
            return redirect("/")
        return render_template("class.html",streak=fun.get_user_streak(),xp=fun.get_user_xp(),notifications=fun.get_notifications(),teacher=fun.check_teacher(classid),userID=fun.get_user_id(),username=fun.get_username(),settings=fun.get_users_settings(),page="class"+classid,classes=fun.get_user_classes(),user_class=user_class,classid=classid)
    return redirect("/")

@app.route("/classroom/<classid>/settings")
def class_settings(classid):
    if fun.login():
        if not fun.check_teacher(classid):
            return redirect("/classroom/"+classid)
        user_class = fun.get_class_without_users_tasks(classid)
        return render_template("class_settings.html",username=fun.get_username(),userID=fun.get_user_id(),settings=fun.get_users_settings(),streak=fun.get_user_streak(),xp=fun.get_user_xp(),notifications=fun.get_notifications(),page="class"+classid,classes=fun.get_user_classes(),user_class=user_class,classid=classid)
    return redirect("/")

@app.route("/task/<classid>/<taskid>")
def task(classid,taskid):
    if fun.login():
        task = None
        if fun.check_teacher(classid):
            user_class = fun.get_user_classes_one_class(classid)
            for i in user_class["tasks"]:
                if i["id"] == taskid:
                    task = i
                    break
            return render_template("viewTask.html",task=task,username=fun.get_username(),userID=fun.get_user_id(),settings=fun.get_users_settings(),streak=fun.get_user_streak(),xp=fun.get_user_xp(),notifications=fun.get_notifications(),page="task"+taskid,classes=fun.get_user_classes(),user_class=user_class,classid=classid,taskid=taskid)
        fun.create_task_student(classid,taskid)
        user_class = fun.get_user_classes_one_class(classid)
        class_color = user_class["classInfo"]["coverImage"]
        for i in user_class["tasks"]:
            if i["id"] == taskid:
                task = i
                break
        code = fun.get_code(classid,taskid,fun.get_id())
        fun.update_streak()
        return render_template("task.html",userid=fun.get_user_id(),username=fun.get_username(),userID=fun.get_user_id(),settings=fun.get_users_settings(),streak=fun.get_user_streak(),xp=fun.get_user_xp(),notifications=fun.get_notifications(),page="task"+taskid,classes=fun.get_user_classes(),class_color=class_color,task=task,classid=classid,taskid=taskid,code=code,teacher=False)
    return redirect("/")

@app.route("/view/<classid>/<taskid>/<userid>")
def view_task(classid,taskid,userid):
    if fun.login():
        if fun.check_teacher(classid):
            user_class = fun.get_user_classes_one_class(classid)
            class_color = user_class["classInfo"]["coverImage"]
            for i in user_class["tasks"]:
                if i["id"] == taskid:
                    task = i
                    break
            code = fun.get_code(classid,taskid,userid)
            return render_template("task.html",username=fun.get_username(),userID=fun.get_user_id(),settings=fun.get_users_settings(),streak=fun.get_user_streak(),xp=fun.get_user_xp(),notifications=fun.get_notifications(),page="task"+taskid,classes=fun.get_user_classes(),class_color=class_color,task=task,classid=classid,taskid=taskid,code=code,teacher=True,userid=userid)
            
@app.route("/join/classroom")
def join_classroom():
    if fun.login():
        return render_template("join_class.html",username=fun.get_username(),userID=fun.get_user_id(),settings=fun.get_users_settings(),streak=fun.get_user_streak(),xp=fun.get_user_xp(),notifications=fun.get_notifications(),page="join classroom",classes=fun.get_user_classes())
    return redirect("/")

@app.route("/settings")
def settings():
    if fun.login():
        return render_template("settings/main.html",username=fun.get_username(),userID=fun.get_user_id(),settings=fun.get_users_settings(),streak=fun.get_user_streak(),xp=fun.get_user_xp(),notifications=fun.get_notifications(),page="settings",classes=fun.get_user_classes())
    return redirect("/")

@app.route("/weakTopics")
def weak_topics_page():
    if fun.login():
        if fun.get_weak_topics(fun.get_user_id()) == "nwt":
            fun.send_notification("You do not have any weak topics yet.","wanning")
            return redirect("/")
        return render_template("weakTopics.html",streak=fun.get_user_streak(),xp=fun.get_user_xp(),notifications=fun.get_notifications(),weakTopics=fun.get_weak_topics(fun.get_user_id()),username=fun.get_username(),userID=fun.get_user_id(),settings=fun.get_users_settings(),page="weak topics",classes=fun.get_user_classes())
    return redirect("/")

@app.route("/tasklist")
def task_list():
    if fun.login():
        return render_template("taskList.html",username=fun.get_username(),userID=fun.get_user_id(),settings=fun.get_users_settings(),streak=fun.get_user_streak(),xp=fun.get_user_xp(),notifications=fun.get_notifications(),page="task list",classes=fun.get_user_classes())
    return redirect("/")

@app.route("/createIdea")
def task_summary():
    if fun.login():
        return render_template("createIdea.html",username=fun.get_username(),userID=fun.get_user_id(),settings=fun.get_users_settings(),streak=fun.get_user_streak(),xp=fun.get_user_xp(),notifications=fun.get_notifications(),page="idea creator",classes=fun.get_user_classes())
    return redirect("/")

@app.route("/learningPath")
def learning_path():
    if fun.login():
        return render_template("learningPath.html",username=fun.get_username(),userID=fun.get_user_id(),settings=fun.get_users_settings(),streak=fun.get_user_streak(),xp=fun.get_user_xp(),notifications=fun.get_notifications(),page="learning path",classes=fun.get_user_classes(),weak_topics=fun.get_weak_topics(fun.get_user_id()))
    return redirect("/")

@app.route("/learningPathTask")
def learning_path_topic():
    if fun.login():
        fun.update_streak()
        return render_template("learningPathTask.html",username=fun.get_username(),userID=fun.get_user_id(),settings=fun.get_users_settings(),streak=fun.get_user_streak(),xp=fun.get_user_xp(),notifications=fun.get_notifications(),page="learning path",classes=fun.get_user_classes())
    return redirect("/")

@app.route("/settings/ai")
def ai_settings():
    if fun.login():
        return render_template("settings/ai.html",username=fun.get_username(),userID=fun.get_user_id(),settings=fun.get_users_settings(),streak=fun.get_user_streak(),xp=fun.get_user_xp(),notifications=fun.get_notifications(),page="AI settings",classes=fun.get_user_classes())
    return redirect("/")

@app.route("/settings/accessibility")
def accessibility_settings():
    if fun.login():
        return render_template("settings/accessibility.html",username=fun.get_username(),userID=fun.get_user_id(),settings=fun.get_users_settings(),streak=fun.get_user_streak(),xp=fun.get_user_xp(),notifications=fun.get_notifications(),page="Accessibility settings",classes=fun.get_user_classes())
    return redirect("/")

@app.route("/settings/account")
def account_settings():
    if fun.login():
        return render_template("settings/account.html",username=fun.get_username(),userID=fun.get_user_id(),settings=fun.get_users_settings(),streak=fun.get_user_streak(),xp=fun.get_user_xp(),notifications=fun.get_notifications(),page="Account settings",classes=fun.get_user_classes())
    return redirect("/")

@app.route("/upgrade/organization")
def upgrade_organization():
    if fun.login():
        return render_template("upgradePages/organizationUpgrade.html",username=fun.get_username(),userID=fun.get_user_id(),settings=fun.get_users_settings(),streak=fun.get_user_streak(),xp=fun.get_user_xp(),notifications=fun.get_notifications(),page="upgrade organization",classes=fun.get_user_classes())
    return redirect("/")

@app.route("/endpoint/settings/ai",methods=["POST"])
def save_ai_settings():
    if fun.login():
        data = request.json
        status = fun.save_ai_settings(data["WeakTopics"],data["TaskSummary"],data["IdeaCreator"],data["LearningPath"])
        return {'status':status}

@app.route("/endpoint/account/delete",methods=["POST"])
def delete_account():
    if fun.login():
        status = fun.delete_account_info()
        return {'status':status}

@app.route("/endpoint/task/edit", methods=["POST"])
def edit_task():    
    if fun.login():
        data = request.json
        if (data["name"] == "" or data["instructions"] == "" or data["date"] == ""):
            return {'status': 'Fill out all fields'}
        elif (len(data["name"]) > 20 or len(data["instructions"]) > 1000):
            return {'status': 'Inputs are values are too long'}
        try:
            task_date = datetime.strptime(data["date"], "%Y-%m-%d")
            if task_date < datetime.now():
                return {'status': 'Date cannot be in the past'}
        except ValueError:
            return {'status': 'Invalid date format. Use YYYY-MM-DD'}
        status = fun.edit_task(data["classid"], data["taskid"], data["name"], data["instructions"], data["date"])
        return {'status': status}
    return  404

@app.route("/endpoint/class/leave",methods=["POST"])
def leave_class():
    if fun.login():
        data = request.json
        status = fun.leave_classroom(data["classid"])
        return {'status':status}
    return  404

@app.route("/endpoint/classroom/delete",methods=["POST"])
def delete_classroom():
    if fun.login():
        data = request.json
        status = fun.delete_classroom(data["classid"])
        return {'status':status}
    return  404


@app.route("/endpoint/task/complete/<classid>/<taskid>")
def complete_task(classid,taskid):
    if fun.login():
        fun.complete_task_student(classid,taskid)
        return redirect("/classroom/"+classid)
    return  404

@app.route("/endpoint/classroom/join",methods=["POST"])
def join_classroom_endpoint():
    if fun.login():
        data = request.json
        if data["classCode"] == "":
            return {'status':'Fill out all fields'}
        elif len(data["classCode"]) > 20:
            return {'status':'Code is too long'}
        status = fun.join_classroom(data["classCode"])
        return {'status':status}
    return  404

@app.route("/endpoint/classroom/save",methods=["POST"])
def save_classroom_settings():
    if fun.login():
        data = request.json
        if (data["name"] == "" or data["subtitle"] == "" or data["description"] == ""):
            return {'status':'Fill out all fields'}
        elif (len(data["name"]) > 20 or len(data["subtitle"]) > 20 or len(data["description"]) > 100):
            return {'status':'Inputs are values are too long'}
        status = fun.save_classroom_settings(data["classid"],data["name"],data["subtitle"],data["description"],data["messageLock"],data["classColor"])
        return {'status':status}
    return  404

@app.route("/endpoint/task/save",methods=["POST"])
def save_task():
    if fun.login():
        data = request.json
        status = fun.save_code(data["classid"],data["taskid"],data["code"])
        return "{'status':"+status+"}"
    return  404

@app.route("/endpoint/task/delete",methods=["POST"])
def delete_task():
    if fun.login():
        data = request.json
        status = fun.delete_task(data["classid"],data["taskid"])
        print(status)
        return {'status':status}
    return  404

@app.route("/endpoint/ai/getweaktopics",methods=["GET"])
def get_weak_topics():
    if fun.login():
        userid = fun.get_id()
        print("User ID",userid)
        data = fun.get_weak_topics(userid)
        return jsonify(data)
    return  404

@app.route("/endpoint/ai/weaktopics",methods=["POST"])
def weak_topics():
    if fun.login():
        userid = fun.get_id()
        print("User ID",userid)
        data = request.json
        data = data["result"]
        fun.weak_topics(userid,data)
        return "complete"
    return  404

@app.route("/endpoint/auth/login",methods=["POST"])
def login_endpoint():
    form = loginForm()
    session.permanent = True
    form_data = request.form
    username = form_data["username"]
    password = fun.password_hash(form_data["password"])
    error = fun.login_user(username,password)
    if error != "Success":
        return render_template("auth/login.html",error=error,form=form)
    return redirect("/")

@app.route("/endpoint/class/create",methods=["POST"])
def create_class():
    if fun.login():
        data = request.json
        if (data["name"] == "" or data["subtitle"] == "" or data["description"] == "" or data["color"] == ""):
            return {'status':'Fill out all fields'}
        elif (len(data["name"]) > 20 or len(data["subtitle"]) > 20 or len(data["description"]) > 100):
            return {'status':'Inputs are values are too long'}
        elif fun.check_amount_of_classes():
            return {'status':'You have reached the maximum amount of classes'}
        classID = fun.create_class(data["name"],data["subtitle"],data["description"],data["color"])
        return {'status':'complete','classId':classID}
    return  404

@app.route("/endpoint/task/create",methods=["POST"])
def create_task_endpoint():
    if fun.login():
        data = request.json
        if (data["name"] == "" or data["description"] == "" or data["date"] == "" or data["points"] == ""):
            return {'status':'Fill out all fields'}
        elif (len(data["name"]) > 20 or len(data["description"]) > 1000):
            return {'status':'Inputs are values are too long'}
        elif (int(data["points"]) < 1 or int(data["points"]) > 100):
            return {'status':'Points must be between 0 and 100'}
        elif fun.check_amount_of_tasks(data["classid"]):
            return {'status':'You have reached the maximum amount of tasks'}
        try:
            task_date = datetime.strptime(data["date"], "%Y-%m-%d")
            if task_date < datetime.now():
                return {'status':'Date cannot be in the past'}
        except ValueError:
            return {'status':'Invalid date format. Use YYYY-MM-DD'}
        fun.create_task(data["classid"],data["name"],data["description"],data["date"],data["points"])
        return {'status':'complete'}
    return  404

@app.route("/endpoint/class/message",methods=["POST"])
def send_message():
    if fun.login():
        data = request.json
        if data["message"] == "":
            return {'status':'Fill out all fields'}
        elif len(data["message"]) > 100:
            return {'status':'Message is too long'}
        elif fun.check_amount_of_messages(data["classid"]):
            return {'status':'You have reached the maximum amount of messages'}
        message = fun.send_message(data["classid"],data["message"])
        return {'status':'complete',"userName":message["userName"],"message":message["message"],"messageId":message["messageId"],"date":message["date"]}
    return  404

@app.route("/endpoint/class/message/delete",methods=["POST"])
def delete_message():
    if fun.login():
        data = request.json
        message = fun.delete_message(data["classid"],data["messageid"])
        return {'status':message}
    return  404

@app.route("/endpoint/task/feedback",methods=["POST"])
def task_feedback():
    if fun.login():
        data = request.json
        if len(data["feedback"]) > 1000:
            return {'status':'Feedback is too long'}
        feedback = fun.task_feedback(data["classid"],data["taskid"],data["feedback"],data["points"],data["userid"])
        return {'status':'complete'}
    return  404

@app.route("/login", methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def login_page():
    form = loginForm()
    if request.method == "POST":
        if form.validate_on_submit():
            username = form.username.data
            password = fun.password_hash(form.password.data)
            error = fun.login_user(username,password)
            if error != "Success":
                return render_template("auth/login.html",error=error,form=form)
            else:
                return redirect("/")
        return render_template("auth/login.html",error="Inputs Invalid",form=form)
    return render_template("auth/login.html",error=False,form=form)

@app.route("/signup", methods=['GET', 'POST'])
def signup_page():
    form = signupForm()
    if request.method == "POST":
        if form.validate_on_submit():
            username = form.username.data
            session.permanent = True
            password = fun.password_hash(form.password.data)
            confirmPassword = fun.password_hash(form.confirmPassword.data)
            error = fun.signup_user(username,password,confirmPassword)
            if error != "Success":
                return render_template("auth/signup.html",error=error,form=form)
            else:
                return redirect("/")
        return render_template("auth/signup.html",error="Inputs Not Valid",form=form)
    return render_template("auth/signup.html",error=False,form=form)

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
    fun.create_account_google(users_name,unique_id,users_email)
    return redirect("/")


@app.errorhandler(404)
def page_not_found(error):
    if fun.login():
        return render_template('404.html', username=fun.get_username(),settings=fun.get_users_settings(), classes=fun.get_user_classes(),page="404"), 404
    return render_template('404.html'), 404

@app.errorhandler(RateLimitExceeded)
def ratelimit_handler(e):
    form = loginForm()
    return render_template(
        "auth/login.html",
        error="Too many login attempts.",form=form
    ), 429

if __name__ == "__main__":
    app.run(debug=True)






