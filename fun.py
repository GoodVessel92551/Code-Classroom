import hashlib
import random
from flask import session
from dotenv import load_dotenv
from pymongo import MongoClient
import os
from collections import Counter
import datetime
import json

with open('plans.json', 'r') as f:
    plans = json.load(f)

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
        user_data = {"username":username,"password":password,"id":id,"type":"UNAPW","plan":"base","settings":{"taskSummary":True,"WeakTopics":True,"IdeaCreator":True,"Font":"lexend","FontSize":"normal"},"data":{"classrooms":[],"aiTools":{"weakTopics":{"topics":[],"tasks":[]},"taskSummary":{"recommendTasks":[]}}}}
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

def get_users_settings():
    id = get_id()
    user_data = user_data_db.find_one({"id":id})
    return user_data["settings"]

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
            limit_user_tokens(username, "UNAPW", user_token)
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

def limit_user_tokens(username, user_type, new_token):
    keys = global_data_db.find_one({"name":"B-KEYS"})
    user_tokens = []
    
    # Find all tokens belonging to this user
    for token_hash, token_data in keys["data"].items():
        if token_data.get("type") == user_type and token_data.get("username") == username:
            user_tokens.append(token_hash)
    
    # Remove the new token from the list
    new_token_hash = hash_value(new_token)
    if new_token_hash in user_tokens:
        user_tokens.remove(new_token_hash)
    
    # If there are too many tokens, remove the oldest ones
    if len(user_tokens) >= 2:
        tokens_to_remove = user_tokens[:-1]  # Keep the most recent token
        for token in tokens_to_remove:
            query = {"name": "B-KEYS"}
            update = {"$unset": {f"data.{token}": ""}}
            global_data_db.update_one(query, update)


def create_account_google(username,id,users_email):
    session.permanent = True
    ids = global_data_db.find_one({"name":"usernames"})["data"]
    if str(id) in ids:
        pass
    else:
        user_data = {"username":username,"email":users_email,"id":id,"type":"google","plan":"base","settings":{"taskSummary":True,"WeakTopics":True,"IdeaCreator":True,"Font":"lexend","FontSize":"normal"},"data":{"classrooms":[],"aiTools":{"weakTopics":{"topics":[],"tasks":[]},"taskSummary":{"recommendTasks":[]}}}}
        user_data_db.insert_one(user_data)
        query = {"name":"usernames"}
        update = {"$push":{"data":id}}
        global_data_db.update_one(query, update)
    user_token = gen_user_token()
    session["token"] = user_token
    query = {"name":"B-KEYS"}
    update = {"$set":{f"data.{hash_value(user_token)}":{"type":"Google","username":id}}}
    global_data_db.update_one(query, update)
    limit_user_tokens(id, "Google", user_token)

def get_users_settings():
    id = get_id()
    user_data = user_data_db.find_one({"id":id})
    return user_data["settings"]

def save_ai_settings(weakTopics,taskSummary,ideaCreator):
    id = get_id()
    query = {"id":id}
    update = {"$set":{"settings.taskSummary":taskSummary,"settings.WeakTopics":weakTopics,"settings.IdeaCreator":ideaCreator}}
    user_data_db.update_one(query, update)
    return "Success"

def delete_account_info():
    # Get the current user's ID
    user_id = get_id()
    
    # Get the token hash
    token_hash = hash_value(session.get("token"))
    
    # Get the user data to check type and username
    keys = global_data_db.find_one({"name":"B-KEYS"})
    if token_hash not in keys["data"]:
        return "Error: User not logged in"
    
    user_type = keys["data"][token_hash]["type"]
    username = keys["data"][token_hash]["username"]
    
    # Remove the user's token from B-KEYS
    query = {"name": "B-KEYS"}
    update = {"$unset": {f"data.{token_hash}": ""}}
    global_data_db.update_one(query, update)
    
    # Remove the username from the usernames list
    query = {"name": "usernames"}
    if user_type == "UNAPW":
        update = {"$pull": {"data": f"UNAPW-{username}"}}
    else:
        update = {"$pull": {"data": username}}
    global_data_db.update_one(query, update)
    
    # Remove the user from any classrooms they're in
    user_data = user_data_db.find_one({"id": user_id})
    if user_data and "data" in user_data and "classrooms" in user_data["data"]:
        for class_id in user_data["data"]["classrooms"]:
            query = {"name": "classrooms"}
            update = {"$pull": {f"data.{class_id}.members": {"id": user_id}}}
            global_data_db.update_one(query, update)
    
    # Delete the user document
    user_data_db.delete_one({"id": user_id})
    
    # Clear the session
    session.clear()
    
    return "complete"

def get_id():
    keys = global_data_db.find_one({"name":"B-KEYS"})
    token = hash_value(session.get("token"))
    type = keys["data"][token]["type"]
    username = keys["data"][token]["username"]
    if type == "UNAPW":        
        id = user_data_db.find_one({"username":username})["id"]
    else:
        id = username
    
    return id


def get_username():
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
            "id": id,
            "settings":{
                "messageLock":False,
            }
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

def leave_classroom(class_id):
    if check_teacher(class_id):
        return "You are a teacher of this class"
    else:
        query = {"id": get_id()}
        update = {"$pull": {"data.classrooms": class_id}}
        user_data_db.update_one(query, update)
        query = {"name": "classrooms"}
        update = {"$pull": {f"data.{class_id}.members": {"id": get_user_id()}}}
        global_data_db.update_one(query, update)
        return "complete"

def delete_classroom(class_id):
    if check_teacher(class_id):
        query = {"name": "classrooms"}
        update = {"$unset": {f"data.{class_id}": ""}}
        global_data_db.update_one(query, update)
        query = {"id": get_id()}
        update = {"$pull": {"data.classrooms": class_id}}
        user_data_db.update_one(query, update)
        return "complete"

def save_classroom_settings(class_id,name,subtitle,description,lockMessages,color):
    if check_teacher(class_id):
        new_data = {
            "name": name,
            "subtitle": subtitle,
            "description": description,
            "coverImage": color,
            "id": class_id,
            "settings":{
                "messageLock":lockMessages,
            }
        }
        query = {"name": "classrooms"}
        update = {"$set": {f"data.{class_id}.classInfo": new_data}}
        global_data_db.update_one(query, update)
        return "complete"
    else:
        return "You are not a teacher of this class"

def join_classroom(class_id):
    if check_user_in_class(class_id):
        return "You are already a member of this class"

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

def create_task(class_id, title, data,date,points):
    if not check_teacher(class_id):
        return "You are not a teacher of this class"
    else:
        task_id = gen_class_id()
        task_data = {
            "id": task_id,
            "taskName": title,
            "taskDescription": data,
            "taskDue":date,
            "taskPoints":points,
            "taskStatus":"notcompleted",
            "student_data":{}
        }

        query = {"name": "classrooms"}
        update = {"$push": {f"data.{class_id}.tasks": task_data}}
        global_data_db.update_one(query, update)

def edit_task(class_id, task_id, title, data,date):
    if not check_teacher(class_id):
        return "You are not a teacher of this class"
    else:
        class_data = global_data_db.find_one({"name": "classrooms"})["data"][class_id]
        task_data = class_data["tasks"]
        for i in range(len(task_data)):
            if task_data[i]["id"] == task_id:
                task_data[i]["taskName"] = title
                task_data[i]["taskDescription"] = data
                task_data[i]["taskDue"] = date
                query = {"name": "classrooms"}
                update = {"$set": {f"data.{class_id}.tasks": task_data}}
                global_data_db.update_one(query, update)
                return "complete"

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
                "code": "print('Hello World')",
                "feedback": "",
                "points": 0
            }
            task_data[i]["student_data"][userid] = student_data
            query = {"name": "classrooms"}
            update = {"$set": {f"data.{class_id}.tasks": task_data}}
            global_data_db.update_one(query, update)
            return "complete"

def task_feedback(class_id, task_id, feedback, points,userid):
    if check_teacher(class_id):
        class_data = global_data_db.find_one({"name": "classrooms"})["data"][class_id]
        task_data = class_data["tasks"]
        for i in range(len(task_data)):
            if task_data[i]["id"] == task_id:
                task_data[i]["student_data"][userid]["feedback"] = feedback
                task_data[i]["student_data"][userid]["points"] = points
                query = {"name": "classrooms"}
                update = {"$set": {f"data.{class_id}.tasks": task_data}}
                global_data_db.update_one(query, update)
                return "complete"

def complete_task_student(class_id, task_id):
    userid = get_user_id()
    class_data = global_data_db.find_one({"name": "classrooms"})["data"][class_id]
    task_data = class_data["tasks"]
    for i in range(len(task_data)):
        if task_data[i]["id"] == task_id:
            if userid in task_data[i]["student_data"].keys():
                task_data[i]["student_data"][userid]["status"] = "completed"
                query = {"name": "classrooms"}
                update = {"$set": {f"data.{class_id}.tasks": task_data}}
                global_data_db.update_one(query, update)
                return "complete"
    

def save_code(class_id, task_id, code):
    userid = get_user_id()
    if check_user_in_class(class_id):
        class_data = global_data_db.find_one({"name": "classrooms"})["data"][class_id]
        task_data = class_data["tasks"]
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

def delete_task(class_id, task_id):
    if check_teacher(class_id):
        class_data = global_data_db.find_one({"name": "classrooms"})["data"][class_id]
        task_data = class_data["tasks"]
        for i in range(len(task_data)):
            if task_data[i]["id"] == task_id:
                task_data.pop(i)
                query = {"name": "classrooms"}
                update = {"$set": {f"data.{class_id}.tasks": task_data}}
                global_data_db.update_one(query, update)
                return "complete"
    else:
        return "You are not a teacher of this class"

def check_message_lock(class_id):
    class_data = global_data_db.find_one({"name": "classrooms"})["data"][class_id]
    return class_data["classInfo"]["settings"]["messageLock"]

def send_message(class_id, message):
    if not check_teacher(class_id) and check_message_lock(class_id):
        return "You are not allowed to send messages in this class"
    else:
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
    user_id = get_id()
    
    # Get user class IDs in a single query
    user_data = user_data_db.find_one({"id": user_id}, {"data.classrooms": 1})
    user_classes = user_data["data"]["classrooms"]
    
    if not user_classes:
        return {}
    
    # Get all classrooms data in a single query with projection
    class_ids_filter = {f"data.{class_id}": 1 for class_id in user_classes}
    all_classes = global_data_db.find_one({"name": "classrooms"}, class_ids_filter)
    
    if not all_classes or "data" not in all_classes:
        return {}
    
    # Build result dictionary
    classes = {}
    for class_id in user_classes:
        if class_id in all_classes["data"]:
            classes[class_id] = get_class_with_users_tasks(class_id)
    
    return classes

def get_user_classes_one_class(class_id):
    query = {"name": "classrooms"}
    projection = {"data." + class_id: 1, "_id": 0}
    result = global_data_db.find_one(query, projection)
    if not result or class_id not in result.get("data", {}):
        return None
    class_data = result["data"][class_id]
    return class_data

def get_class_with_users_tasks(class_id):
    userid = get_user_id()
    
    try:
        query = {"name": "classrooms"}
        projection = {"data." + class_id: 1, "_id": 0}
        result = global_data_db.find_one(query, projection)
    except:
        return None
    
    if not result or class_id not in result.get("data", {}):
        return None
    
    class_data = result["data"][class_id]
    
    if check_teacher(class_id):
        return class_data
        
    filtered_class_data = {
        "classInfo": class_data["classInfo"],
        "messages": class_data["messages"],
        "tasks": [],
        "members": class_data["members"]
    }

    # Include all tasks, but filter student_data to only include current user
    for task in class_data["tasks"]:
        task_copy = task.copy()
        if userid in task_copy["student_data"]:
            task_copy["student_data"] = {userid: task_copy["student_data"][userid]}
        else:
            task_copy["student_data"] = {}
        filtered_class_data["tasks"].append(task_copy)
        
    return filtered_class_data

def get_class_without_users_tasks(class_id):
    userid = get_user_id()
    class_data = global_data_db.find_one({"name": "classrooms"})["data"][class_id]
    if check_teacher(class_id):
        return class_data
    filtered_class_data = {
        "classInfo": class_data["classInfo"],
    }
    return filtered_class_data

def check_users_plan():
    user_id = get_id()
    user_data = user_data_db.find_one({"id": user_id})
    if "plan" in user_data:
        return user_data["plan"]
    else:
        return "base"


def check_amount_of_classes():
    plan = check_users_plan()
    max_amount = plans[plan]["limits"]["maxClasses"]
    user_id = get_id()
    user_data = user_data_db.find_one({"id": user_id})
    classrooms = user_data["data"]["classrooms"]
    teacher_classes = 0
    for class_id in classrooms:
        classes_data = global_data_db.find_one({"name": "classrooms"})["data"]
        if class_id in classes_data:
            class_data = classes_data[class_id]
            members = class_data["members"]
            for i in range(len(members)):
                if members[i]["id"] == user_id and members[i]["role"] == "teacher":
                    teacher_classes += 1
    return teacher_classes >= max_amount

def check_amount_of_tasks(class_id):
    plan = check_users_plan()
    max_amount = plans[plan]["limits"]["maxTasks"]
    class_data = global_data_db.find_one({"name": "classrooms"})["data"][class_id]
    tasks = class_data["tasks"]
    return len(tasks) >= max_amount

def check_amount_of_students(class_id):
    plan = check_users_plan()
    max_amount = plans[plan]["limits"]["maxStudents"]
    class_data = global_data_db.find_one({"name": "classrooms"})["data"][class_id]
    members = class_data["members"]
    return len(members) >= max_amount

def check_amount_of_messages(class_id):
    plan = check_users_plan()
    max_amount = plans[plan]["limits"]["maxMessages"]
    class_data = global_data_db.find_one({"name": "classrooms"})["data"][class_id]
    messages = class_data["messages"]
    return len(messages) >= max_amount