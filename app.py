import os
from datetime import datetime

from flask import Flask, render_template, request, url_for, redirect, make_response, session, send_from_directory

from requester import Requester

app = Flask(__name__)

requester = Requester()


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'icon.png', mimetype='image/png')


def add_user_to_session(user_id, user_key):
    db_request = requester.make_request(
        {"account": {"type": "session",
                     "user_id": user_id, "key": user_key},
         "object": {"type": "account",
                    "id": user_id},
         "action": "get"})

    user = db_request["objects"]
    if user:
        session["user"] = user[0]
    return user


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
        return redirect(url_for("login"))


@app.route("/user")
def user_home():
    keys = check_session()
    if keys:
        user_id, user_key = keys
        db_request = requester.make_request(
            {"account": {"type": "session",
                         "user_id": user_id, "key": user_key},
             "object": {"type": "account",
                        "id": user_id},
             "action": "get"})
        user = db_request["objects"][0]
        return render_template("user_home.html", user=user)
    else:
        return redirect(url_for("index"))


@app.route("/user/<id>")
def user(id):
    keys = check_session()
    if keys:
        user_id, user_key = keys
        if int(id) == user_id:
            return redirect(url_for("user_home"))

        db_request = requester.make_request(
            {"account": {"type": "session",
                         "user_id": user_id, "key": user_key},
             "object": {"type": "account",
                        "id": int(id)},
             "action": "get"})

        user = db_request["objects"][0]

        db_request = requester.make_request(
            {"account": {"type": "session",
                         "user_id": user_id, "key": user_key},
             "object": {"type": "follow",
                        "followed": user["id"],
                        "follower": user_id,
                        "following": "follow_account"},
             "action": "get"})

        if db_request["objects"]:
            user["followed"] = "true"
        else:
            user["followed"] = "false"

        return render_template("user.html", user=user)
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
            return redirect(url_for("login"))
        return render_template('register.html', info=response["error"])
    return render_template('register.html')


@app.route("/user/login", methods=["GET", "POST"])
def login():
    if check_session():
        return redirect(url_for("index"))

    if request.method == "POST":
        login = request.form["login"]
        password = request.form["password"]
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
                 "object": {"type": "session", "user_id": user_id},
                 "action": "get"})
            user_key = get_session_request["objects"][0]["key"]

            response = make_response(redirect("/"))
            response.set_cookie('user_id', str(user_id))
            response.set_cookie('user_key', user_key)
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

        db_request = requester.make_request(
            {"account": {"type": "session",
                         "user_id": user_id, "key": user_key},
             "object": {"type": "list",
                        "user_id": user_id},
             "action": "get"})
        if db_request["status"] != "handled":
            return render_template("lists_menu.html", error=db_request["error"])
        upcomming_lists = db_request["objects"]
        for one_list in upcomming_lists:
            one_list["author"] = session["user"]["nick"]
        upcomming_lists.sort(key=lambda x: convert_str_to_date(x["date"]), reverse=True)
        if upcomming_lists:
            units.append({"name": "latest", "lists": upcomming_lists})

        followeds_lists = get_followeds_lists(user_id, user_key)
        add_author_to_list(user_id, user_key, followeds_lists)
        followeds_lists.sort(key=lambda x: convert_str_to_date(x["date"]), reverse=True)
        if followeds_lists:
            units.append({"name": "followed", "lists": followeds_lists})

        return render_template("lists_menu.html", units=units)
    else:
        return redirect(url_for("index"))


def get_followeds_lists(user_id, user_key):
    lists = []

    result = requester.make_request(
        {"account": {"type": "session",
                     "user_id": user_id, "key": user_key},
         "object": {"type": "follow",
                    "follower": user_id,
                    "following": "follow_account"},
         "action": "get"})
    followeds_ids = [x["followed"] for x in result["objects"]]
    for one_id in followeds_ids:
        db_request = requester.make_request(
            {"account": {"type": "session",
                         "user_id": user_id, "key": user_key},
             "object": {"type": "list",
                        "user_id": one_id},
             "action": "get"})
        lists.extend(db_request["objects"])

    result = requester.make_request(
        {"account": {"type": "session",
                     "user_id": user_id, "key": user_key},
         "object": {"type": "follow",
                    "follower": user_id,
                    "following": "follow_group"},
         "action": "get"})
    followeds_ids = [x["followed"] for x in result["objects"]]
    for one_id in followeds_ids:
        db_request = requester.make_request(
            {"account": {"type": "session",
                         "user_id": user_id, "key": user_key},
             "object": {"type": "list",
                        "group_id": one_id},
             "action": "get"})
        lists.extend(db_request["objects"])
    return lists


def add_author_to_list(user_id, user_key, lists):
    for list in lists:
        if "user_id" in list:
            get_account_request = requester.make_request(
                {"account": {"type": "session",
                             "user_id": user_id, "key": user_key},
                 "object": {"type": "account", "id": list["user_id"]},
                 "action": "get"})
            if get_account_request["objects"]:
                if "user_id" in list:
                    list["author"] = get_account_request["objects"][0]["nick"]
                else:
                    list["author"] = get_account_request["objects"][0]["id"]
            else:
                list["author"] = "deleted"
        else:
            list["author"] = "anonymous"
    return lists


@app.route("/list/followed")
def followed_menu():
    keys = check_session()
    if keys:
        user_id, user_key = keys
        units = []
        lists = get_followeds_lists(user_id, user_key)
        add_author_to_list(user_id, user_key, lists)
        lists.sort(key=lambda x: convert_str_to_date(x["date"]), reverse=True)
        units.append({"name": "lists", "lists": lists})
        return render_template("followed_menu.html", units=units)
    else:
        return redirect(url_for("index"))


@app.route("/list/add", methods=["GET", "POST"])
def list_add():
    keys = check_session()
    if keys:
        user_id, user_key = keys
        if request.method == "POST":
            requests_object = {"type": "list",
                               "user_id": user_id,
                               "name": request.form["name"],
                               "content": request.form["content"]}
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
            result = requester.make_request(
                {"account": {"type": "session",
                             "user_id": user_id, "key": user_key},
                 "object": {"type": "group",
                            "id": group_id},
                 "action": "get"})
            groups.extend(result["objects"])
        return render_template("lists_add.html", groups=groups)
    else:
        return redirect(url_for("index"))


@app.route("/list/<list_id>")
def one_list(list_id):
    keys = check_session()
    if keys:
        user_id, user_key = keys
        db_request = requester.make_request(
            {"account": {"type": "session",
                         "user_id": user_id, "key": user_key},
             "object": {"type": "list",
                        "id": int(list_id)},
             "action": "get"})
        the_list = db_request["objects"][0]
        get_user_request = requester.make_request(
            {"account": {"type": "session",
                         "user_id": user_id, "key": user_key},
             "object": {"type": "account",
                        "id": the_list["user_id"]},
             "action": "get"})
        user = get_user_request["objects"][0]
        the_list["author"] = user
        return render_template("list_id.html", list=the_list)
    else:
        return redirect(url_for("index"))


@app.route("/list/del", methods=["POST"])
def list_del():
    keys = check_session()
    if keys and request.method == "POST":
        user_id, user_key = keys
        requester.make_request(
            {"account": {"type": "session",
                         "user_id": user_id, "key": user_key},
             "object": {"type": "list",
                        "id": int(request.form["id"]),
                        "user_id": user_id,
                        "name": request.form["name"]},
             "action": "del"})
    return redirect(url_for("index"))


@app.route('/search')
def search():
    results = []
    keys = check_session()
    if keys:
        user_id, user_key = keys
        response = requester.make_request(
            {"account": {"type": "session",
                         "user_id": user_id,
                         "key": user_key},
             "object": {"type": "account",
                        "nick": request.args.get("query")},
             "action": "get"})
        for result in response["objects"]:
            result["type"] = "user"
            result["url"] = url_for("user", id=result["id"])
            results.append(result)

        response = requester.make_request(
            {"account": {"type": "session",
                         "user_id": user_id,
                         "key": user_key},
             "object": {"type": "list",
                        "name": request.args.get("query")},
             "action": "get"})
        for result in response["objects"]:
            result["type"] = "list"
            result["url"] = url_for("one_list", list_id=result["id"])
            results.append(result)

        return render_template("search_results.html", results=results, query=request.args.get('query'))
    else:
        return redirect(url_for("index"))


@app.route('/follow/<type>/<id>')
def follow(type, id):
    keys = check_session()
    if keys:
        user_id, user_key = keys
        response = requester.make_request(
            {"account": {"type": "session",
                         "user_id": user_id,
                         "key": user_key},
             "object": {"type": "follow",
                        "followed": int(id),
                        "follower": user_id,
                        "following": "follow_" + type},
             "action": "add"})
        return response["status"]


@app.route('/unfollow/<type>/<id>')
def unfollow(type, id):
    keys = check_session()
    if keys:
        user_id, user_key = keys
        response = requester.make_request(
            {"account": {"type": "session",
                         "user_id": user_id,
                         "key": user_key},
             "object": {"type": "follow",
                        "followed": int(id),
                        "follower": user_id,
                        "following": "follow_" + type},
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
    return redirect(url_for("groups_menu"))


@app.route("/group/<group_id>")
def one_group(group_id):
    keys = check_session()
    if keys:
        user_id, user_key = keys
        get_group_request = requester.make_request(
            {"account": {"type": "session",
                         "user_id": user_id, "key": user_key},
             "object": {"type": "group",
                        "id": int(group_id)},
             "action": "get"})
        group = get_group_request["objects"][0]
        get_lists_request = requester.make_request(
            {"account": {"type": "session",
                         "user_id": user_id, "key": user_key},
             "object": {"type": "list",
                        "group_id": group["id"]},
             "action": "get"})
        lists = get_lists_request["objects"]
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
