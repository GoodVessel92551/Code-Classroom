# load required libraries
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

# load the database connection
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
    # Create a new sha256 hash object
    sha256 = hashlib.sha256()
    sha256.update(str(data).encode('utf-8'))
    return sha256.hexdigest()

def password_hash(password, salt=os.getenv("salt"), iterations=100000, dklen=64, hashfunc=hashlib.sha256):
    """
    Hashes a password and the key.
    Args:
        password (str): The password to be hashed.
        salt (str): The salt to be used in the hashing process. Default is from environment variable "salt".
        iterations (int): The number of iterations for the hashing algorithm. Default is 100000.
        dklen (int): The length of the derived key. Default is 64.
        hashfunc: The hash function to be used. Default is hashlib.sha256.
    Returns:
        bytes: The hashed password.
    """
    # hash the password and key
    key = password.encode('utf-8')
    salt = salt.encode('utf-8')
    return hashlib.pbkdf2_hmac(hashfunc().name, key, salt, iterations, dklen)

def signup_user(username,password,confirmPassword):
    """
    Signs up a new user with the provided username and password.

    Args:
        username (str): The desired username for the new user.
        password (str): The password for the new user.
        confirmPassword (str): The confirmation of the password.

    Returns:
        str: A message indicating the result of the signup process.
             Possible values are:
             - "Username is too short" if the username is less than 2 characters.
             - "Username is too long" if the username is more than 20 characters.
             - "Passwords do not match" if the password and confirmPassword do not match.
             - "Username already exists" if the username is already taken.
             - "Success" if the signup was successful.
    """
    session.permanent = True # make the session permanent so the token lasts longer rather than until the browser is closed
    # check if the username if the username is valid
    if len(username) < 2:
        return "Username is too short"
    elif len(username) > 20:
        return "Username is too long"
    elif password != confirmPassword:
        return "Passwords do not match"
    
    id = gen_user_id()
    ids = global_data_db.find_one({"name":"usernames"})["data"]
    # check if the username already exists
    if str("UNAPW-"+username) in ids:
        return "Username already exists"
    else:
        # create the user and add to the database
        user_data = {"username":username,"password":password,"id":id,
                     "type":"UNAPW","plan":"base","settings":
                     {"taskSummary":True,"WeakTopics":True,"IdeaCreator":True,"learningPath":True,"Font":"lexend","FontSize":"normal"},
                     "data":{"classrooms":[],"aiTools":{"weakTopics":{"topics":[],"tasks":[]},
                     "taskSummary":{"recommendTasks":[]}},"xp":{"level":0,"points":0},"streaks":{"level":0,"streak":0,"lastStreak":datetime.datetime.now().strftime("%Y-%m-%d")}}}
        user_data_db.insert_one(user_data)
        query = {"name":"usernames"}
        update = {"$push":{"data":"UNAPW-"+username}}
        global_data_db.update_one(query, update)
    # log the user and create a session token
    user_token = gen_user_token()
    session["token"] = user_token
    query = {"name":"B-KEYS"}
    update = {"$set":{f"data.{hash_value(user_token)}":{"type":"UNAPW","username":username}}}
    global_data_db.update_one(query, update)
    return "Success"

def login_user(username,password):
    """
    Logs in a user with the provided username and password.
    
    Args:
        username (str): The username of the user attempting to log in.
        password (str): The password of the user attempting to log in.
    Returns:
        str: A message indicating the result of the login process.
             Possible values are:
             - "Success" if the login was successful.
             - "Incorrect Password" if the provided password is incorrect.
             - "Username does not exist" if the username is not found in the database.
    """
    session.permanent = True # make the session permanent so the token lasts longer rather than until the browser is closed
    ids = global_data_db.find_one({"name":"usernames"})["data"]
    # check that username exists
    if str("UNAPW-"+username) in ids:
        user = user_data_db.find_one({"username":username})
        if user["password"] == password:
            # log the user and create a session token
            user_token = gen_user_token()
            session["token"] = user_token
            query = {"name":"B-KEYS"}
            update = {"$set":{f"data.{hash_value(user_token)}":{"type":"UNAPW","username":username}}}
            global_data_db.update_one(query, update)
            limit_user_tokens(username, "UNAPW", user_token) # limit the number of tokens a user can have to 2
            return "Success"
        else:
            return "Incorrect Password"
    else:
        return "Username does not exist"

def gen_user_token():
    """
    Generates a random user token consisting of 20 alphanumeric characters.

    Returns:
        str: A randomly generated user token.
    """
    chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    token = ""
    for i in range(20):
        token += random.choice(chars) # choose a random character from the chars string repeat 20 times
    return token

def gen_user_id():
    """
    Generates a random user token consisting of 15 alphanumeric characters.
    
    Returns:
        str: A randomly generated user id.
    """
    chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    id = "G-"
    for i in range(15):
        id += random.choice(chars) # choose a random character from the chars string repeat 15 times
    return id

def gen_class_id():
    """
    Generates a random user token consisting of 5 to 10 alphanumeric characters.
    
    Returns:
        str: A randomly generated class token.
    """
    chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    id = ""
    for i in range(random.randint(5,10)): # random length between 5 and 10
        id += random.choice(chars) # choose a random character from the chars string repeat 5 to 10 times
    return id

def login():
    """
    Checks if the user is logged in by verifying the session token against the database.
    Returns:
        bool: True if the user is logged in, False otherwise.
    """
    if session.get("token"):
        keys = global_data_db.find_one({"name":"B-KEYS"})
        if str(hash_value(session.get("token"))) in keys["data"]: # check if the user token exists in the database
            return True
    return False

def limit_user_tokens(username, user_type, new_token):
    """
    Limits the number of active tokens for a user to a maximum of 2.

    Args:
        username (str): The username of the user.
        user_type (str): The type of the user (e.g., "UNAPW", "Google").
        new_token (str): The newly generated token for the user.
    """
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
    
    # If there are 2 or more tokens, remove the oldest ones
    if len(user_tokens) >= 2:
        tokens_to_remove = user_tokens[:-1] 
        for token in tokens_to_remove:
            query = {"name": "B-KEYS"}
            update = {"$unset": {f"data.{token}": ""}}
            global_data_db.update_one(query, update)


def create_account_google(username,id,users_email):
    """
    Creates a new user account using Google authentication.

    Args:
        username (str): The username of the user.
        id (str): The unique identifier for the user from Google.
        users_email (str): The email address of the user.

    """
    session.permanent = True
    ids = global_data_db.find_one({"name":"usernames"})["data"] # check that if the user already exists
    if str(id) in ids:
        pass
    else:
        # create the user and add to the database
        user_data = {"username":username,"email":users_email,"id":id,"type":"google","plan":"base","settings":
                     {"taskSummary":True,"WeakTopics":True,"IdeaCreator":True,"learningPath":True,"Font":"lexend","FontSize":"normal"},
                     "data":{"classrooms":[],"aiTools":{"weakTopics":{"topics":[],"tasks":[]},
                     "taskSummary":{"recommendTasks":[]}},"xp":{"level":0,"points":0},
                     "streaks":{"level":0,"streak":0,"lastStreak":datetime.datetime.now().strftime("%Y-%m-%d")}}}
        user_data_db.insert_one(user_data)
        query = {"name":"usernames"}
        update = {"$push":{"data":id}}
        global_data_db.update_one(query, update)
    user_token = gen_user_token()
    session["token"] = user_token
    query = {"name":"B-KEYS"}
    update = {"$set":{f"data.{hash_value(user_token)}":{"type":"Google","username":id}}}
    global_data_db.update_one(query, update)
    limit_user_tokens(id, "Google", user_token) # limit the number of tokens a user can have to 2

def get_users_settings():
    """
    Retrieves the settings of the currently logged-in user.

    Returns:
        dict: A dictionary containing the user's settings.
    """
    id = get_id()
    user_data = user_data_db.find_one({"id":id}) # get the user data from the database

    if "learningPath" not in user_data["settings"]:
        user_data_db.update_one({"id": id}, {"$set": {"settings.learningPath": True}})
        user_data["settings"]["learningPath"] = True
    return user_data["settings"]

def save_ai_settings(weakTopics,taskSummary,ideaCreator,learningPath):
    """
    Saves the AI-related settings for the currently logged-in user.
    Args:
        weakTopics (bool): Whether the weak topics feature is enabled.
        taskSummary (bool): Whether the task summary feature is enabled.
        ideaCreator (bool): Whether the idea creator feature is enabled.
        learningPath (bool): Whether the learning path feature is enabled.

    Returns:
        str: A message indicating the result of the save operation ("Success").
    """
    id = get_id()
    query = {"id":id}
    update = {"$set":{"settings.taskSummary":taskSummary,"settings.WeakTopics":weakTopics,"settings.IdeaCreator":ideaCreator,"settings.learningPath":learningPath}}
    user_data_db.update_one(query, update)
    return "Success"

def delete_account_info():
    """
    Deletes the account information of the currently logged-in user.
    
    Returns:
        str: A message indicating the result of the deletion process ("complete" or an error message).
    """
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

def send_notification(title, error_type):
    """
    Sends a notification to the user by storing it in the session.
    
    Args:
        title (str): The title of the notification.
        error_type (str): The type of the notification (e.g., "error", "success").
    """
    notification = {
        "title": title,
        "type": error_type,
    } # create a notification object
    session["notification"].append(notification) # append the notification to the session

def get_notifications():
    """
    Retrieves and clears the notifications stored in the session.
    
    Returns:
        list: A list of notifications.
        
    """
    if "notification" not in session:
        session["notification"] = []
    notifications = session.get("notification")
    session["notification"] = []
    return notifications


def get_id():
    """
    Retrieves the ID of the currently logged-in user based on the session token.
    Returns:
        str: The ID of the logged-in user.
    """
    keys = global_data_db.find_one({"name":"B-KEYS"})
    token = hash_value(session.get("token"))
    type = keys["data"][token]["type"]
    username = keys["data"][token]["username"] # get the username from the token
    if type == "UNAPW":   # check if user is using username and password     
        id = user_data_db.find_one({"username":username})["id"] # get the id from the username
    else:
        id = username # for google users, the username is the id
    
    return id


def get_username():
    """
    Retrieves the username of the currently logged-in user.

    Returns:
        str: The user's username.
    """
    username = user_data_db.find_one({"id":str(get_id())})["username"]
    return username

def get_user_streak():
    """
    Retrieves the user's streak data, initializing it if missing.

    Returns:
        dict: Dictionary with keys level, streak, lastStreak (YYYY-MM-DD).
    """
    user_id = get_id()
    user_data = user_data_db.find_one({"id": user_id})
    
    # Check if the streaks field exists in the user data
    if "data" not in user_data or "streaks" not in user_data.get("data", {}):
        # Initialize streaks if it doesn't exist
        query = {"id": user_id}
        update = {"$set": {"data.streaks": {"level": 0, "streak": 0,"lastStreak":datetime.datetime.now().strftime("%Y-%m-%d")}}}
        user_data_db.update_one(query, update)
        return {"level": 0, "streak": 0,"lastStreak":datetime.datetime.now().strftime("%Y-%m-%d")}
    
    return user_data["data"]["streaks"]

def get_user_xp():
    """
    Retrieves the user's XP data, initializing it if missing.

    Returns:
        dict: Dictionary with keys level and points.
    """
    user_id = get_id()
    user_data = user_data_db.find_one({"id": user_id})
    print(user_data.get("data", {}))
    if "data" not in user_data or "xp" not in user_data.get("data", {}):
        print("XP not found")
        user_data_db.update_one({"id": user_id}, {"$set": {"data.xp": {"level": 0, "points": 0}}})
        return {"level": 0, "points": 0}
    return user_data["data"]["xp"]

def increase_xp(points):
    """
    Increases the user's XP by a number of points and handles level-up.

    Args:
        points (int): Points to add.

    Returns:
        str: "complete" when done.
    """
    user_id = get_id()
    user_data = user_data_db.find_one({"id": user_id})
    xp = user_data["data"]["xp"]
    xp["points"] += points
    if xp["points"] >= 100:
        xp["level"] += 1
        xp["points"] -= 100
    print(xp)
    query = {"id": user_id}
    update = {"$set": {"xp": xp}}
    user_data_db.update_one(query, update)
    return "complete"

def update_streak():
    """
    Updates the user's daily streak, granting XP and adjusting level as needed.

    Returns:
        str: "complete" when processed.
    """
    streak = get_user_streak()
    last_streak = streak["lastStreak"]
    current_date = datetime.datetime.now().strftime("%Y-%m-%d")
    
    if last_streak == current_date:
        return "complete"
    
    last_date = datetime.datetime.strptime(last_streak, "%Y-%m-%d")
    current_datetime = datetime.datetime.strptime(current_date, "%Y-%m-%d")
    
    yesterday = current_datetime - datetime.timedelta(days=1)
    
    if last_date.date() == yesterday.date():
        streak["streak"] += 1
        increase_xp(2)
        set_streak_level()
    else:
        streak["streak"] = 0
    
    streak["lastStreak"] = current_date
    
    query = {"id": get_id()}
    update = {"$set": {"data.streaks": streak}}
    user_data_db.update_one(query, update)
    
    return "complete"

def set_streak_level():
    """
    Sets streak level based on current streak count and grants milestone XP.

    Returns:
        str: "complete" after updating.
    """
    streak = get_user_streak()
    streak_level = streak["level"]
    streak_level_old = streak_level
    streak_count = streak["streak"]

    if streak_count >= 10:
        streak_level = 1
        increase_xp(10)
    elif streak_count >= 20:
        streak_level = 2
        increase_xp(20)
    elif streak_count >= 30:
        streak_level = 3
        increase_xp(30)
    elif streak_count >= 40:
        streak_level = 4
        increase_xp(35)
    elif streak_count >= 50:
        streak_level = 5
        increase_xp(40)
    elif streak_count >= 60:
        streak_level = 6
        increase_xp(45)
    elif streak_count >= 70:
        streak_level = 7
        increase_xp(50)
    elif streak_count >= 80:
        streak_level = 8
        increase_xp(52)
    elif streak_count >= 90:
        streak_level = 9
        increase_xp(55)
    elif streak_count >= 100:
        increase_xp(57)
        streak_level = 10

    if streak_level != streak_level_old:
        streak_count = 0

    query = {"id": get_id()}
    update = {"$set": {"data.streaks.level": streak_level, "data.streaks.streak": streak_count}}
    user_data_db.update_one(query, update)
    
    return "complete"


def weak_topics(id,data):
    """
    Adds a weak topic entry for a user.

    Args:
        id (str): User id.
        data (str): Topic label to add.

    Returns:
        str: "Success" after saving.
    """
    user_data = user_data_db.find_one({"id":id})
    topics = user_data["data"]["aiTools"]["weakTopics"]["topics"]
    topics.append(data)
    query = {"id":id}
    update = {"$set":{"data.aiTools.weakTopics.topics":topics}}
    user_data_db.update_one(query, update)
    return "Success"

def get_weak_topics(id):
    """
    Returns the two most common weak topics for a user.

    Args:
        id (str): User id.

    Returns:
        str | list[tuple[str, int]]: "nwt" if none, else top 2 as (topic, count).
    """
    user_data = user_data_db.find_one({"id":id})
    topics = user_data["data"]["aiTools"]["weakTopics"]["topics"]
    if len(topics) == 0:
        return "nwt"
    counter = Counter(topics)
    return counter.most_common(2)

def get_user_id():
    """
    Returns the database id of the currently logged-in user.

    Returns:
        str: The current user's id.
    """
    return user_data_db.find_one({"id":get_id()})["id"]


def create_class(name, subtitle, description, color):
    """
    Creates a classroom owned by the current user (as teacher).

    Args:
        name (str): Class name.
        subtitle (str): Class subtitle.
        description (str): Class description.
        color (str): Cover image key.

    Returns:
        str: Created class id.
    """
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
    """
    Removes the current user from a classroom if they are not a teacher.

    Args:
        class_id (str): Class id.

    Returns:
        str: "complete" or error message.
    """
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
    """
    Deletes a classroom if the current user is its teacher.

    Args:
        class_id (str): Class id.

    Returns:
        str: "complete" when removed.
    """
    if check_teacher(class_id):
        query = {"name": "classrooms"}
        update = {"$unset": {f"data.{class_id}": ""}}
        global_data_db.update_one(query, update)
        query = {"id": get_id()}
        update = {"$pull": {"data.classrooms": class_id}}
        user_data_db.update_one(query, update)
        return "complete"

def save_classroom_settings(class_id, name, subtitle, description, lockMessages, color):
    """
    Saves classroom settings if the current user is the teacher.

    Args:
        class_id (str): Class id.
        name (str): New class name.
        subtitle (str): New subtitle.
        description (str): New description.
        lockMessages (bool): Lock messages for students.
        color (str): Cover image key.

    Returns:
        str: "complete" or error message.
    """
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
    """
    Adds the current user to a classroom as a student.

    Args:
        class_id (str): Class id.

    Returns:
        str: "complete" or error string.
    """
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
    """
    Checks if the current user is a teacher in the class.

    Args:
        class_id (str): Class id.

    Returns:
        bool: True if teacher, else False.
    """
    user_id = get_user_id()
    class_data = global_data_db.find_one({"name": "classrooms"})["data"][class_id]
    members = class_data["members"]
    for i in range(len(members)):
        if members[i]["id"] == user_id and members[i]["role"] == "teacher":
            return True
    return False

def check_user_in_class(class_id):
    """
    Checks if the current user is a member of the class.

    Args:
        class_id (str): Class id.

    Returns:
        bool: True if member, else False.
    """
    user_id = get_user_id()
    class_data = global_data_db.find_one({"name": "classrooms"})["data"][class_id]
    members = class_data["members"]
    for i in range(len(members)):
        if members[i]["id"] == user_id:
            return True
    return False

def create_task(class_id, title, data, date, points):
    """
    Creates a task in the class (teacher only).

    Args:
        class_id (str): Class id.
        title (str): Task title.
        data (str): Task description.
        date (str): Due date (YYYY-MM-DD).
        points (int): Points value.

    Returns:
        None | str: Error string if not permitted.
    """
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
            "student_data":{},
            "type":"task"
        }

        query = {"name": "classrooms"}
        update = {"$push": {f"data.{class_id}.tasks": task_data}}
        global_data_db.update_one(query, update)

def create_resource(class_id, title, data):
    """
    Creates a resource in the class (teacher only).

    Args:
        class_id (str): Class id.
        title (str): Resource title.
        data (str): Resource markdown/content.

    Returns:
        None | str: Error string if not permitted.
    """
    if not check_teacher(class_id):
        return "You are not a teacher of this class"
    else:
        resource_id = gen_class_id()
        resource_data = {
            "id": resource_id,
            "taskName": title,
            "taskDescription": data,
            "type":"resource",
            "tags":[]
        }

        query = {"name": "classrooms"}
        update = {"$push": {f"data.{class_id}.tasks": resource_data}}
        global_data_db.update_one(query, update)

def create_poll(class_id, title, options):
    """
    Creates a poll in the class (teacher only).

    Args:
        class_id (str): Class id.
        title (str): Poll title.
        options (list[str]): Options to include.

    Returns:
        None | str: Error string if not permitted.
    """
    if not check_teacher(class_id):
        return "You are not a teacher of this class"
    else:
        for i in range(len(options)):
            options[i] = {"option":options[i],"votes":0}
        poll_id = gen_class_id()
        poll_data = {
            "id": poll_id,
            "taskName": title,
            "options": options,
            "voters": [],
            "type":"poll"
        }

        query = {"name": "classrooms"}
        update = {"$push": {f"data.{class_id}.tasks": poll_data}}
        global_data_db.update_one(query, update)

def vote_poll(class_id, poll_id, vote):
    """
    Records a user's vote on a poll if they haven't voted yet.

    Args:
        class_id (str): Class id.
        poll_id (str): Poll id.
        vote (str): Selected option.

    Returns:
        dict | str: Updated poll data or error string.
    """
    userid = get_user_id()
    class_data = global_data_db.find_one({"name": "classrooms"})["data"][class_id]
    task_data = class_data["tasks"]
    for i in range(len(task_data)):
        if task_data[i]["id"] == poll_id:
            if userid in task_data[i]["voters"]:
                return "You have already voted"
            task_data[i]["voters"].append(userid)
            for j in range(len(task_data[i]["options"])):
                if task_data[i]["options"][j]["option"] == vote:
                    task_data[i]["options"][j]["votes"] += 1
            query = {"name": "classrooms"}
            update = {"$set": {f"data.{class_id}.tasks": task_data}}
            global_data_db.update_one(query, update)
            return task_data[i]

def edit_task(class_id, task_id, title, data, date):
    """
    Edits a task (teacher only).

    Args:
        class_id (str): Class id.
        task_id (str): Task id.
        title (str): New title.
        data (str): New description.
        date (str): New due date.

    Returns:
        str: "complete" when saved.
    """
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
    """
    Initializes a student's task data for a given task.

    Args:
        class_id (str): Class id.
        task_id (str): Task id.

    Returns:
        str: "complete" or error string.
    """
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

def task_feedback(class_id, task_id, feedback, points, userid):
    """
    Saves teacher feedback and points for a student's task.

    Args:
        class_id (str): Class id.
        task_id (str): Task id.
        feedback (str): Feedback text.
        points (int): Awarded points.
        userid (str): Student user id.

    Returns:
        str: "complete" when saved.
    """
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
    """
    Marks the current user's task as completed.

    Args:
        class_id (str): Class id.
        task_id (str): Task id.

    Returns:
        str: "complete" when updated.
    """
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
    """
    Saves code for the current user on a specific task.

    Args:
        class_id (str): Class id.
        task_id (str): Task id.
        code (str): Source code to save.

    Returns:
        str: "complete" when saved.
    """
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

def get_code(class_id, task_id, userid):
    """
    Retrieves saved code for a given user and task.

    Args:
        class_id (str): Class id.
        task_id (str): Task id.
        userid (str): User id to fetch code for.

    Returns:
        str: Saved code content.
    """
    if check_user_in_class(class_id):
        class_data = global_data_db.find_one({"name": "classrooms"})["data"][class_id]
        task_data = class_data["tasks"]
        for i in range(len(task_data)):
            if task_data[i]["id"] == task_id:
                student_data = task_data[i]["student_data"]
                return student_data[userid]["code"]

def delete_task(class_id, task_id):
    """
    Deletes a task from the class (teacher only).

    Args:
        class_id (str): Class id.
        task_id (str): Task id.

    Returns:
        str: "complete" or error string.
    """
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
    """
    Checks whether messages are locked for students in the class.

    Args:
        class_id (str): Class id.

    Returns:
        bool: True if locked, else False.
    """
    class_data = global_data_db.find_one({"name": "classrooms"})["data"][class_id]
    return class_data["classInfo"]["settings"]["messageLock"]

def send_message(class_id, message,messageImportant):
    """
    Sends a message to the class, respecting message lock for students.

    Args:
        class_id (str): Class id.
        message (str): Message text.
        messageImportant (bool): Marks message as important.

    Returns:
        dict | str: The saved message dict or error string.
    """
    if not check_teacher(class_id) and check_message_lock(class_id):
        return "You are not allowed to send messages in this class"
    else:
        message = {
            "userName": get_username(),
            "message": message,
            "messageId": gen_class_id(),
            "date": datetime.datetime.now().strftime("%Y-%m-%d"),
            "userID": get_user_id(),
            "messageImportant":messageImportant
        }

        query = {"name": "classrooms"}
        update = {"$push": {f"data.{class_id}.messages": message}}
        global_data_db.update_one(query, update)
        return message

def delete_message(class_id, message_id):
    """
    Deletes a message if the user is teacher or the message author.

    Args:
        class_id (str): Class id.
        message_id (str): Message id.

    Returns:
        str: "complete" or error string.
    """
    if check_teacher(class_id) or check_user_sent_message(class_id, message_id):
        pass
    else:
        return "You are not allowed to delete this message"
    query = {"name": "classrooms"}
    update = {"$pull": {f"data.{class_id}.messages": {"messageId": message_id}}}
    global_data_db.update_one(query, update)
    return "complete"


def check_user_sent_message(class_id, message_id):
    """
    Checks if the current user authored a specific message.

    Args:
        class_id (str): Class id.
        message_id (str): Message id.

    Returns:
        bool: True if user is author, else False.
    """
    messages = global_data_db.find_one({"name": "classrooms"})["data"][class_id]["messages"]
    for i in range(len(messages)):
        if messages[i]["messageId"] == message_id and messages[i]["userID"] == get_user_id():
            return True
    return False


def get_user_classes():
    """
    Retrieves all classes for the current user with appropriate task filtering.

    Returns:
        dict: Map of class_id to class data.
    """
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
    """
    Retrieves a single class document by id.

    Args:
        class_id (str): Class id.

    Returns:
        dict | None: Class data or None if not found.
    """
    query = {"name": "classrooms"}
    projection = {"data." + class_id: 1, "_id": 0}
    result = global_data_db.find_one(query, projection)
    if not result or class_id not in result.get("data", {}):
        return None
    class_data = result["data"][class_id]
    return class_data

def get_class_with_users_tasks(class_id):
    """
    Retrieves class data, filtering task student_data to the current user (if student).

    Args:
        class_id (str): Class id.

    Returns:
        dict | None: Filtered class data or None on error/not found.
    """
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

    for task in class_data["tasks"]:
        task_copy = task.copy()
        if "type" in task_copy:
            if task_copy["type"] != "task":
                filtered_class_data["tasks"].append(task_copy)
            else:
                if userid in task_copy["student_data"]:
                    task_copy["student_data"] = {userid: task_copy["student_data"][userid]}
                else:
                    task_copy["student_data"] = {}
                filtered_class_data["tasks"].append(task)
        else:
            if userid in task_copy["student_data"]:
                task_copy["student_data"] = {userid: task_copy["student_data"][userid]}
            else:
                task_copy["student_data"] = {}
            filtered_class_data["tasks"].append(task)
    return filtered_class_data

def get_class_without_users_tasks(class_id):
    """
    Retrieves class information without including tasks (for non-teachers).

    Args:
        class_id (str): Class id.

    Returns:
        dict: Class info only.
    """
    userid = get_user_id()
    class_data = global_data_db.find_one({"name": "classrooms"})["data"][class_id]
    if check_teacher(class_id):
        return class_data
    filtered_class_data = {
        "classInfo": class_data["classInfo"],
    }
    return filtered_class_data

def check_users_plan():
    """
    Gets the current user's subscription plan.

    Returns:
        str: Plan name (e.g., "base").
    """
    user_id = get_id()
    user_data = user_data_db.find_one({"id": user_id})
    if "plan" in user_data:
        return user_data["plan"]
    else:
        return "base"


def check_amount_of_classes():
    """
    Checks whether the user has reached their plan's maximum number of teacher classes.

    Returns:
        bool: True if at or above limit, else False.
    """
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
    """
    Checks whether the class is at the plan's task limit.

    Args:
        class_id (str): Class id.

    Returns:
        bool: True if at or above limit, else False.
    """
    plan = check_users_plan()
    max_amount = plans[plan]["limits"]["maxTasks"]
    class_data = global_data_db.find_one({"name": "classrooms"})["data"][class_id]
    tasks = class_data["tasks"]
    tasksNum = 0
    for i in range(len(tasks)):
        if "type" in tasks[i]:
            if tasks[i]["type"] == "task":
                tasksNum += 1
        else:
            tasksNum += 1
    return tasksNum >= max_amount

def check_amount_of_students(class_id):
    """
    Checks whether the class is at the plan's student limit.

    Args:
        class_id (str): Class id.

    Returns:
        bool: True if at or above limit, else False.
    """
    plan = check_users_plan()
    max_amount = plans[plan]["limits"]["maxStudents"]
    class_data = global_data_db.find_one({"name": "classrooms"})["data"][class_id]
    members = class_data["members"]
    return len(members) >= max_amount

def check_amount_of_messages(class_id):
    """
    Checks whether the class is at the plan's messages limit.

    Args:
        class_id (str): Class id.

    Returns:
        bool: True if at or above limit, else False.
    """
    plan = check_users_plan()
    max_amount = plans[plan]["limits"]["maxMessages"]
    class_data = global_data_db.find_one({"name": "classrooms"})["data"][class_id]
    messages = class_data["messages"]
    return len(messages) >= max_amount

def check_amount_of_polls(classid):
    """
    Checks whether the class is at the plan's polls limit.

    Args:
        classid (str): Class id.

    Returns:
        bool: True if at or above limit, else False.
    """
    plan = check_users_plan()
    max_amount = plans[plan]["limits"]["maxPolls"]
    class_data = global_data_db.find_one({"name": "classrooms"})["data"][classid]
    tasks = class_data["tasks"]
    polls = 0
    for i in range(len(tasks)):
        if "type" in tasks[i]:
            if tasks[i]["type"] == "poll":
                polls += 1
    return polls >= max_amount

def check_amount_of_resources(classid):
    """
    Checks whether the class is at the plan's resources limit.

    Args:
        classid (str): Class id.

    Returns:
        bool: True if at or above limit, else False.
    """
    plan = check_users_plan()
    max_amount = plans[plan]["limits"]["maxResources"]
    class_data = global_data_db.find_one({"name": "classrooms"})["data"][classid]
    tasks = class_data["tasks"]
    resources = 0
    for i in range(len(tasks)):
        if "type" in tasks[i]:
            if tasks[i]["type"] == "resource":
                resources += 1
    return resources >= max_amount

def check_user_in_class(classid):
    """
    Checks whether the current user belongs to the given class.

    Args:
        classid (str): Class id.

    Returns:
        bool: True if member, else False.
    """
    user_id = get_user_id()
    class_data = global_data_db.find_one({"name": "classrooms"})["data"][classid]
    members = class_data["members"]
    for i in range(len(members)):
        if members[i]["id"] == user_id:
            return True
    return False