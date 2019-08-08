import json
import os
from datetime import datetime

from flask import Flask, render_template, request, url_for, redirect, make_response, session, send_from_directory

from requester import Requester

app = Flask(__name__)

requester = Requester()


@app.errorhandler(500)
def page_internal_error(e):
    return render_template("500_error.html"), 500


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'icon.png', mimetype='image/png')


def add_user_to_session(user_id, user_key):
    the_user = get_objects_by_field(user_id, user_key, "account", user_id)[0]
    if the_user:
        session["user"] = the_user
    return the_user


def check_session():
    if "user_id" in request.cookies.keys() and "user_key" in request.cookies.keys():
        user_id = int(request.cookies.get("user_id"))
        user_key = request.cookies.get("user_key")
        session['logged'] = True
        if "user" not in session.keys():
            if not add_user_to_session(user_id, user_key):
                return None
        return user_id, user_key
    session['logged'] = False
    if 'user' in session.keys():
        session.pop('user')
    return None


def convert_str_to_date(string):
    return datetime.strptime(string, '%Y-%m-%d %H:%M')


@app.route("/")
def index():
    if check_session():
        return redirect(url_for("lists_menu"))
    else:
        return redirect(url_for("log_in"))


@app.route("/user/<the_id>")
def user(the_id):
    keys = check_session()
    if keys:
        user_id, user_key = keys
        the_user = get_objects_by_field(user_id, user_key, "account", int(the_id))[0]

        if int(the_id) != user_id:
            db_request = requester.make_request(
                {"account": {"type": "session",
                             "user_id": user_id, "key": user_key},
                 "object": {"type": "follow",
                            "followed": the_user["id"],
                            "follower": user_id,
                            "following": "follow_account"},
                 "action": "get"})

            if db_request["objects"]:
                the_user["followed"] = "true"
            else:
                the_user["followed"] = "false"

        return render_template("user.html", user=the_user)
    else:
        return redirect(url_for("index"))


@app.route("/user/register", methods=["GET", "POST"])
def register():
    if check_session():
        return redirect(url_for("index"))
    if request.method == "POST":
        response = requester.make_request(
            {"account": {"type": "anonymous"},
             "object": {"type": "account",
                        "nick": request.form["nick"],
                        "login": request.form["login"],
                        "password": request.form["password"]},
             "action": "add"})
        if response["status"] == "handled":
            return redirect(url_for("log_in"))
        return render_template('register.html', info=response["error"])
    return render_template('register.html')


@app.route("/user/login", methods=["GET", "POST"])
def log_in():
    if check_session():
        return redirect(url_for("index"))
    if request.method == "POST":
        login = str(request.form["login"])
        password = str(request.form["password"])
        get_user_request = requester.make_request(
            {"account": {"type": "anonymous"},
             "object": {"type": "account",
                        "login": login,
                        "password": password},
             "action": "get"})

        if "objects" not in get_user_request:
            return render_template("login.html", error='server error')

        if not get_user_request["objects"]:
            return render_template("login.html", error='account not found')

        user_id = get_user_request["objects"][0]["id"]

        add_session_request = requester.make_request(
            {"account": {"type": "account",
                         "login": login,
                         "password": password},
             "object": {"type": "session", "user_id": user_id},
             "action": "add"})

        if add_session_request["status"] == "handled":
            get_session_request = requester.make_request(
                {"account": {"type": "account",
                             "login": login,
                             "password": password},
                 "object": {"type": "session",
                            "user_id": user_id},
                 "action": "get"})

            user_key = get_session_request["objects"][-1]["key"]

            response = make_response(redirect("/"))
            response.set_cookie('user_id', str(user_id))
            response.set_cookie('user_key', str(user_key))
            return response
        else:
            return render_template("login.html", error=add_session_request["error"])

    return render_template("login.html")


@app.route("/user/logout")
def logout():
    keys = check_session()
    response = make_response(redirect(url_for("index")))
    if keys:
        response.set_cookie('user_id', '', expires=0)
        response.set_cookie('user_key', '', expires=0)
    return response


@app.route("/list")
def lists_menu():
    keys = check_session()
    if keys:
        user_id, user_key = keys
        units = []

        units.extend(get_user_lists_units(user_id, user_key))

        units.extend(get_followed_lists_units(user_id, user_key))

        units.extend(get_followed_accounts_lists_units(user_id, user_key))

        units.extend(get_followed_groups_lists_units(user_id, user_key))

        return render_template("lists_menu.html", units=units)
    else:
        return redirect(url_for("index"))


def get_followed_groups_lists_units(user_id, user_key):
    units = []
    followed_groups_lists = get_followed_groups_list(user_id, user_key)
    for the_follow in followed_groups_lists:
        if the_follow["lists"]:
            group = get_objects_by_field(user_id, user_key, "group", the_follow["group_id"])
            if group:
                lists = the_follow["lists"]
                add_author_to_list(user_id, user_key, lists)
                lists.sort(key=lambda x: convert_str_to_date(x["date"]), reverse=True)
                group_name = group[0]["name"]
                units.append(
                    {"name": group_name, "lists": lists, "url": url_for("one_group", group_id=group[0]["id"])})
    return units


def get_followed_accounts_lists_units(user_id, user_key):
    units = []
    followed_accounts_lists = get_followed_accounts_lists(user_id, user_key)
    for the_follow in followed_accounts_lists:
        if the_follow["lists"]:
            account = get_objects_by_field(user_id, user_key, "account", the_follow["account_id"])[0]
            if account:
                lists = the_follow["lists"]
                add_author_to_list(user_id, user_key, lists)
                lists.sort(key=lambda x: convert_str_to_date(x["date"]), reverse=True)
                account_name = account["nick"] + "`s"
                units.append({"name": account_name, "lists": lists, "url": url_for("user", the_id=account["id"])})
    return units


def get_followed_lists_units(user_id, user_key):
    units = []
    followed_lists = get_followed_lists(user_id, user_key)
    if followed_lists:
        add_author_to_list(user_id, user_key, followed_lists)
        followed_lists.sort(key=lambda x: convert_str_to_date(x["date"]), reverse=True)
        units.append({"name": "followed", "lists": followed_lists, "url": url_for("followed_lists")})
    return units


def get_user_lists_units(user_id, user_key):
    units = []
    user_lists = get_objects_by_field(user_id, user_key, "list", user_id, "user_id")
    if user_lists:
        for the_list in user_lists:
            the_list["author"] = session["user"]
        user_lists.sort(key=lambda x: convert_str_to_date(x["date"]), reverse=True)
        units.append({"name": session["user"]["nick"], "lists": user_lists, "url": url_for("user", the_id=user_id)})
    return units


def get_objects_by_field(user_id, user_key, object_type, object_field_value, object_field_name="id"):
    db_request = requester.make_request(
        {"account": {"type": "session",
                     "user_id": user_id, "key": user_key},
         "object": {"type": object_type,
                    object_field_name: object_field_value},
         "action": "get"})
    return db_request["objects"]


def get_followed_lists(user_id, user_key):
    lists = []

    result = requester.make_request(
        {"account": {"type": "session",
                     "user_id": user_id, "key": user_key},
         "object": {"type": "follow",
                    "follower": user_id,
                    "following": "follow_list"},
         "action": "get"})
    followed_ids = [x["followed"] for x in result["objects"]]
    for one_id in followed_ids:
        db_request = get_objects_by_field(user_id, user_key, "list", one_id)
        lists.extend(db_request)
    return lists


def get_followed_groups_list(user_id, user_key):
    lists = []
    result = requester.make_request(
        {"account": {"type": "session",
                     "user_id": user_id, "key": user_key},
         "object": {"type": "follow",
                    "follower": user_id,
                    "following": "follow_group"},
         "action": "get"})

    followed_ids = [x["followed"] for x in result["objects"]]
    for one_id in followed_ids:
        db_request = get_objects_by_field(user_id, user_key, "list", one_id, "group_id")
        lists.append({"group_id": one_id, "lists": db_request})
    return lists


def get_followed_accounts_lists(user_id, user_key):
    lists = []
    result = requester.make_request(
        {"account": {"type": "session",
                     "user_id": user_id, "key": user_key},
         "object": {"type": "follow",
                    "follower": user_id,
                    "following": "follow_account"},
         "action": "get"})

    followed_ids = [x["followed"] for x in result["objects"]]
    for one_id in followed_ids:
        db_request = get_objects_by_field(user_id, user_key, "list", one_id, "user_id")
        lists.append({"account_id": one_id, "lists": db_request})
    return lists


def add_author_to_list(user_id, user_key, lists):
    for the_list in lists:
        if "user_id" in the_list:
            get_account_request = get_objects_by_field(user_id, user_key, "account", the_list["user_id"])
            if get_account_request:
                the_list["author"] = get_account_request[0]
        else:
            the_list["author"] = "anonymous"
    return lists


def add_group_to_list(user_id, user_key, lists):
    for the_list in lists:
        if "group_id" in the_list:
            get_group_request = get_objects_by_field(user_id, user_key, "group", the_list["group_id"])[0]
            if get_group_request:
                the_list["group"] = get_group_request["objects"][0]["name"]
            else:
                the_list["group"] = "deleted"
        else:
            the_list["group"] = None
    return lists


@app.route("/list/followed")
def followed_lists():
    keys = check_session()
    if keys:
        user_id, user_key = keys
        units = []
        lists = get_followed_lists(user_id, user_key)
        add_author_to_list(user_id, user_key, lists)
        lists.sort(key=lambda x: convert_str_to_date(x["date"]), reverse=True)
        units.append({"name": "lists", "lists": lists})
        return render_template("followed_lists.html", units=units)
    else:
        return redirect(url_for("index"))


@app.route("/list/add", methods=["GET", "POST"])
def list_add():
    keys = check_session()
    if keys:
        user_id, user_key = keys
        if request.method == "POST" or request.method == "post":
            requests_object = {"type": "list",
                               "user_id": user_id,
                               "name": request.form["name"],
                               "content": request.form["content"]}
            print(requests_object["content"])
            if request.form["visibility"] != "none":
                requests_object["group_id"] = request.form["visibility"]

            db_request = requester.make_request(
                {"account": {"type": "session",
                             "user_id": user_id, "key": user_key},
                 "object": requests_object,
                 "action": "add"})
            if db_request["status"] == "handled":
                return redirect(url_for("lists_menu"))
            else:
                return render_template("lists_add.html", error=db_request["error"])
        get_group_follows_request = requester.make_request(
            {"account": {"type": "session",
                         "user_id": user_id, "key": user_key},
             "object": {"type": "follow",
                        "follower": user_id,
                        "following": "follow_group"},
             "action": "get"})
        followed_groups_ids = [x["followed"] for x in get_group_follows_request["objects"]]
        groups = []
        for group_id in followed_groups_ids:
            result = get_objects_by_field(user_id, user_key, "group", group_id)
            groups.extend(result)
        return render_template("lists_add.html", groups=groups)
    else:
        return redirect(url_for("index"))


@app.route("/list/<list_id>")
def one_list(list_id):
    keys = check_session()
    if keys:
        user_id, user_key = keys
        the_list = get_objects_by_field(user_id, user_key, "list", int(list_id))[0]
        the_user = get_objects_by_field(user_id, user_key, "account", the_list["user_id"])[0]
        the_list["author"] = the_user

        follow_response = requester.make_request(
            {"account": {"type": "session",
                         "user_id": user_id,
                         "key": user_key},
             "object": {"type": "follow",
                        "followed": int(list_id),
                        "follower": user_id,
                        "following": "follow_list"},
             "action": "get"})
        if follow_response["objects"]:
            the_list["followed"] = "true"
        else:
            the_list["followed"] = "false"
        return render_template("one_list.html", list=the_list)
    else:
        return redirect(url_for("index"))


@app.route("/list/del", methods=["POST"])
def list_del():
    try:
        keys = check_session()
        if keys and (request.method == "POST" or request.method == "post"):
            user_id, user_key = keys
            requester.make_request(
                {"account": {"type": "session",
                             "user_id": user_id, "key": user_key},
                 "object": {"type": "list",
                            "id": int(request.form["id"]),
                            "user_id": user_id,
                            "name": request.form["name"]},
                 "action": "del"})
    except Exception as e:
        return e
    return redirect(url_for("index"))


@app.route('/search')
def search():
    results = []
    keys = check_session()
    if keys:
        user_id, user_key = keys
        response = get_objects_by_field(user_id, user_key, "account", request.args.get("query"), "nick")
        for result in response:
            result["type"] = "user"
            result["url"] = url_for("user", the_id=result["id"])
            results.append(result)

        response = get_objects_by_field(user_id, user_key, "list", request.args.get("query"), "name")
        for result in response:
            result["type"] = "list"
            result["url"] = url_for("one_list", list_id=result["id"])
            results.append(result)

        response = get_objects_by_field(user_id, user_key, "group", request.args.get("query"), "name")
        for result in response:
            result["type"] = "group"
            result["url"] = url_for("one_group", group_id=result["id"])
            results.append(result)

        return render_template("search_results.html", results=results, query=request.args.get('query'))
    else:
        return redirect(url_for("index"))


@app.route('/follow/<follow_type>/<followed_id>')
def follow(follow_type, followed_id):
    keys = check_session()
    if keys:
        user_id, user_key = keys
        response = requester.make_request(
            {"account": {"type": "session",
                         "user_id": user_id,
                         "key": user_key},
             "object": {"type": "follow",
                        "followed": int(followed_id),
                        "follower": user_id,
                        "following": "follow_" + follow_type},
             "action": "add"})
        return response["status"]


@app.route('/unfollow/<follow_type>/<followed_id>')
def unfollow(follow_type, followed_id):
    keys = check_session()
    if keys:
        user_id, user_key = keys
        response = requester.make_request(
            {"account": {"type": "session",
                         "user_id": user_id,
                         "key": user_key},
             "object": {"type": "follow",
                        "followed": int(followed_id),
                        "follower": user_id,
                        "following": "follow_" + follow_type},
             "action": "del"})
        return response["status"]


@app.route("/group")
def groups_menu():
    keys = check_session()
    if keys:
        user_id, user_key = keys
        result = requester.make_request(
            {"account": {"type": "session",
                         "user_id": user_id,
                         "key": user_key},
             "object": {"type": "group"},
             "action": "get"})
        groups = result["objects"]
        return render_template("groups_menu.html", groups=groups)
    return redirect(url_for("index"))


@app.route('/group/add', methods=["POST"])
def add_group():
    keys = check_session()
    if keys:
        user_id, user_key = keys
        if request.method == "POST":
            requester.make_request(
                {"account": {"type": "session",
                             "user_id": user_id,
                             "key": user_key},
                 "object": {"type": "group",
                            "name": request.form["new_group_name"]},
                 "action": "add"})
            response = get_objects_by_field(user_id, user_key, "group", request.form["new_group_name"], "name")
            follow("group", response[0]["id"])
    return redirect(url_for("groups_menu"))


@app.route("/group/<group_id>")
def one_group(group_id):
    keys = check_session()
    if keys:
        user_id, user_key = keys
        group = get_objects_by_field(user_id, user_key, "group", int(group_id))[0]
        lists = get_objects_by_field(user_id, user_key, "list", group_id, "group_id")

        add_author_to_list(user_id, user_key, lists)

        follow_response = requester.make_request(
            {"account": {"type": "session",
                         "user_id": user_id,
                         "key": user_key},
             "object": {"type": "follow",
                        "followed": group_id,
                        "follower": user_id,
                        "following": "follow_group"},
             "action": "get"})
        if follow_response["objects"]:
            group["followed"] = "true"
        else:
            group["followed"] = "false"

        return render_template("one_group.html", group=group, lists=lists)
    else:
        return redirect(url_for("index"))
