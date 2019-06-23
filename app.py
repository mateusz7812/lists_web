from datetime import datetime

from flask import Flask, render_template, request, url_for, redirect, make_response, session

from requester import Requester

app = Flask(__name__)

requester = Requester()


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
            return redirect("user_home")

        db_request = requester.make_request(
            {"account": {"type": "session",
                         "user_id": user_id, "key": user_key},
             "object": {"type": "account",
                        "id": int(id)},
             "action": "get"})

        user = db_request["objects"][0]

        db_request = requester.make_request(
            {"account": {"type": "account",
                         "login": "test",
                         "password": "test"},
             "object": {"type": "follow",
                        "followed": user["id"],
                        "follower": user_id},
             "action": "get"})

        if len(db_request["objects"]):
            user["followed"] = True

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
            units.append({"name": "upcoming", "lists": upcomming_lists})

        followeds_lists = get_followeds_lists(user_id, user_key)
        add_author_to_list(user_id, user_key, followeds_lists)
        followeds_lists.sort(key=lambda x: convert_str_to_date(x["date"]), reverse=True)
        if followeds_lists:
            units.append({"name": "followed`s", "lists": followeds_lists})

        return render_template("lists_menu.html", units=units)
    else:
        return redirect(url_for("index"))


def get_followeds_lists(user_id, user_key):
    result = requester.make_request(
        {"account": {"type": "session",
                     "user_id": user_id, "key": user_key},
         "object": {"type": "follow",
                    "follower": user_id},
         "action": "get"})
    followeds_ids = [x["followed"] for x in result["objects"]]
    lists = []
    for one_id in followeds_ids:
        db_request = requester.make_request(
            {"account": {"type": "session",
                         "user_id": user_id, "key": user_key},
             "object": {"type": "list",
                        "user_id": one_id},
             "action": "get"})
        lists.extend(db_request["objects"])
    return lists


def add_author_to_list(user_id, user_key, lists):
    for list in lists:
        get_account_request = requester.make_request(
            {"account": {"type": "session",
                         "user_id": user_id, "key": user_key},
             "object": {"type": "account", "id": list["user_id"]},
             "action": "get"})
        list["author"] = get_account_request["objects"][0]["nick"]
    return lists


@app.route("/list/followed")
def followers_lists():
    keys = check_session()
    if keys:
        user_id, user_key = keys
        lists = get_followeds_lists(user_id, user_key)
        add_author_to_list(user_id, user_key, lists)
        lists.sort(key=lambda x: convert_str_to_date(x["date"]), reverse=True)
        return render_template("lists_followeds.html", lists=lists)
    else:
        return redirect(url_for("index"))


@app.route("/list/add", methods=["GET", "POST"])
def list_add():
    keys = check_session()
    if keys:
        if request.method == "POST":
            user_id, user_key = keys
            db_request = requester.make_request(
                {"account": {"type": "session",
                             "user_id": user_id, "key": user_key},
                 "object": {"type": "list",
                            "user_id": user_id,
                            "name": request.form["name"],
                            "content": request.form["content"]},
                 "action": "add"})
            if db_request["status"] == "handled":
                return redirect(url_for("lists_menu"))
            else:
                return render_template("lists_add.html", error=db_request["error"])
        return render_template("lists_add.html")
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
        return render_template("list.html", list=the_list)
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


@app.route('/follow/<id>')
def follow(id):
    keys = check_session()
    if keys:
        user_id, user_key = keys
        response = requester.make_request(
            {"account": {"type": "account",
                         "login": "test",
                         "password": "test"},
             "object": {"type": "follow",
                        "followed": int(id),
                        "follower": user_id},
             "action": "add"})
        return response["status"]


@app.route('/unfollow/<id>')
def unfollow(id):
    keys = check_session()
    if keys:
        user_id, user_key = keys
        response = requester.make_request(
            {"account": {"type": "account",
                         "login": "test",
                         "password": "test"},
             "object": {"type": "follow",
                        "followed": int(id),
                        "follower": user_id},
             "action": "del"})
        return response["status"]
