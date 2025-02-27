import hashlib
import random
from flask import session
from dotenv import load_dotenv
from pymongo import MongoClient
import os
from collections import Counter
import datetime


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
        user_data = {"username":username,"password":password,"id":id,"type":"UNAPW","data":{"classrooms":[],"aiTools":{"weakTopics":{"topics":[],"tasks":[]}}}}
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

def gen_class_id():
    chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    id = ""
    for i in range(random.randint(5,10)):
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
        user_data = {"username":username,"id":id,"type":"google","data":{"classrooms":[],"aiTools":{"weakTopics":{"topics":[],"tasks":[]}}}}
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

def get_weak_topics(id):
    user_data = user_data_db.find_one({"id":id})
    topics = user_data["data"]["aiTools"]["weakTopics"]["topics"]
    counter = Counter(topics)
    return counter.most_common(2)

def get_user_id():
    return user_data_db.find_one({"id":get_id()})["id"]


def create_class(name, subtitle, description, color):
    id = gen_class_id()
    class_data = {
        "classInfo": {
            "name": name,
            "subtitle": subtitle,
            "description": description,
            "coverImage": color,
            "id": id
        },
        "messages": [],
        "tasks": [],
        "members": [{"id": get_user_id(), "role": "teacher","username":get_username()}]
    }
    
    # Update to store class in dictionary using the id as key
    query = {"name": "classrooms"}
    update = {"$set": {f"data.{id}": class_data}}
    global_data_db.update_one(query, update)

    # Update user data to store class id
    query = {"id": get_id()}
    update = {"$push": {"data.classrooms": id}}
    user_data_db.update_one(query, update)


    return id

def join_classroom(class_id):
    # ! need to check if the user is already in the class

    classrooms = global_data_db.find_one({"name": "classrooms"})["data"]
    if class_id in classrooms.keys():
        query = {"id": get_id()}
        update = {"$push": {"data.classrooms": class_id}}
        user_data_db.update_one(query, update)
        classroom = classrooms[class_id]
        members = classroom["members"]
        members.append({"id": get_id(), "role": "student","username":get_username()})
        query = {"name": "classrooms"}
        update = {"$set": {f"data.{class_id}.members": members}}
        global_data_db.update_one(query, update)
        return "complete"
    else:
        return "Class does not exist"

def check_teacher(class_id):
    print(class_id)
    user_id = get_user_id()
    class_data = global_data_db.find_one({"name": "classrooms"})["data"][class_id]
    members = class_data["members"]
    for i in range(len(members)):
        if members[i]["id"] == user_id and members[i]["role"] == "teacher":
            return True
    return False

def check_user_in_class(class_id):
    user_id = get_user_id()
    class_data = global_data_db.find_one({"name": "classrooms"})["data"][class_id]
    members = class_data["members"]
    for i in range(len(members)):
        if members[i]["id"] == user_id:
            return True
    return False

def create_task(class_id, title, data,date):
    print("Class ID "+class_id)
    if not check_teacher(class_id):
        return "You are not a teacher of this class"
    else:
        task_id = gen_class_id()
        task_data = {
            "id": task_id,
            "taskName": title,
            "taskDescription": data,
            "taskDue":date,
            "taskStatus":"notcompleted",
            "student_data":{}
        }

        query = {"name": "classrooms"}
        update = {"$push": {f"data.{class_id}.tasks": task_data}}
        global_data_db.update_one(query, update)

def create_task_student(class_id, task_id):
    userid = get_user_id()
    class_data = global_data_db.find_one({"name": "classrooms"})["data"][class_id]
    task_data = class_data["tasks"]
    for i in range(len(task_data)):
        if task_data[i]["id"] == task_id:
            if userid in task_data[i]["student_data"].keys():
                return "You have already submitted this task"
            student_data = {
                "id": userid,
                "status": "notcompleted",
                "code": "print('Hello World')"
            }
            task_data[i]["student_data"][userid] = student_data
            query = {"name": "classrooms"}
            update = {"$set": {f"data.{class_id}.tasks": task_data}}
            global_data_db.update_one(query, update)
            return "complete"

def save_code(class_id, task_id, code):
    userid = get_user_id()
    print(check_user_in_class(class_id))
    if check_user_in_class(class_id):
        class_data = global_data_db.find_one({"name": "classrooms"})["data"][class_id]
        task_data = class_data["tasks"]
        print("USER IN CLASS")
        for i in range(len(task_data)):
            if task_data[i]["id"] == task_id:
                student_data = task_data[i]["student_data"]
                student_data[userid]["code"] = code
                query = {"name": "classrooms"}
                update = {"$set": {f"data.{class_id}.tasks": task_data}}
                global_data_db.update_one(query, update)
                return "complete"

def get_code(class_id, task_id,userid):
    if check_user_in_class(class_id):
        class_data = global_data_db.find_one({"name": "classrooms"})["data"][class_id]
        task_data = class_data["tasks"]
        for i in range(len(task_data)):
            if task_data[i]["id"] == task_id:
                student_data = task_data[i]["student_data"]
                return student_data[userid]["code"]

def send_message(class_id, message):
    print("Class ID "+class_id)
    print("Message "+message)

    message = {
        "userName": get_username(),
        "message": message,
        "messageId": gen_class_id(),
        "date": datetime.datetime.now().strftime("%Y-%m-%d"),
        "userID": get_user_id()
    }

    query = {"name": "classrooms"}
    update = {"$push": {f"data.{class_id}.messages": message}}
    global_data_db.update_one(query, update)
    return message

def delete_message(class_id, message_id):
    if check_teacher(class_id) or check_user_sent_message(class_id, message_id):
        pass
    else:
        return "You are not allowed to delete this message"
    query = {"name": "classrooms"}
    update = {"$pull": {f"data.{class_id}.messages": {"messageId": message_id}}}
    global_data_db.update_one(query, update)
    return "complete"


def check_user_sent_message(class_id, message_id):
    messages = global_data_db.find_one({"name": "classrooms"})["data"][class_id]["messages"]
    for i in range(len(messages)):
        if messages[i]["messageId"] == message_id and messages[i]["userID"] == get_user_id():
            return True
    return False


def get_user_classes():
    classes = {}
    user_id = get_id()
    user_classes = user_data_db.find_one({"id": user_id})["data"]["classrooms"]
    print(user_classes)
    for i in range(len(user_classes)):
        class_id = user_classes[i]
        if class_id in global_data_db.find_one({"name": "classrooms"})["data"].keys():
            print(class_id)
            class_data = global_data_db.find_one({"name": "classrooms"})["data"][class_id]
            classes[class_id] = class_data
    print(classes)

    return classes
