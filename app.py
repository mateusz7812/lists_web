from flask import Flask, render_template, request, url_for, redirect, make_response, session

from requester import Requester

app = Flask(__name__)

requester = Requester()


def get_user_key():
    if "user_id" in request.cookies.keys() and "user_key" in request.cookies.keys():
        user_id = int(request.cookies.get("user_id"))
        user_key = request.cookies.get("user_key")
        session['logged'] = True
        return user_id, user_key
    session['logged'] = False
    return None


@app.route("/")
def index():
    if get_user_key():
        return redirect(url_for("lists_menu"))
    else:
        return redirect(url_for("login"))


@app.route("/user")
def user_home():
    keys = get_user_key()
    if keys:
        user_id, user_key = keys
        db_request = requester.make_request(
            {"account": {"type": "session",
                         "user_id": user_id, "key": user_key},
             "object": {"type": "account",
                        "id": id},
             "action": "get"})
        return render_template("user_home.html", user=db_request["objects"][0])
    else:
        return redirect(url_for("index"))


@app.route("/user/<id>")
def user(id):
    keys = get_user_key()
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
    if get_user_key():
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
    if get_user_key():
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
    keys = get_user_key()
    response = make_response(redirect(url_for("index")))
    if keys:
        response.set_cookie('user_id', '', expires=0)
        response.set_cookie('user_key', '', expires=0)
    return response


@app.route("/list")
def lists_menu():
    keys = get_user_key()
    if keys:
        user_id, user_key = keys
        db_request = requester.make_request(
            {"account": {"type": "session",
                         "user_id": user_id, "key": user_key},
             "object": {"type": "list",
                        "user_id": user_id},
             "action": "get"})
        if db_request["status"] == "handled":
            return render_template("lists_menu.html", lists=db_request["objects"])
        else:
            return render_template("lists_menu.html", error=db_request["error"])
    else:
        return redirect(url_for("index"))


@app.route("/list/add", methods=["GET", "POST"])
def list_add():
    keys = get_user_key()
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
def list(list_id):
    keys = get_user_key()
    if keys:
        user_id, user_key = keys
        db_request = requester.make_request(
            {"account": {"type": "session",
                         "user_id": user_id, "key": user_key},
             "object": {"type": "list",
                        "id": int(list_id)},
             "action": "get"})
        the_list = db_request["objects"][0]
        return render_template("list.html", list=the_list)
    else:
        return redirect(url_for("index"))


@app.route("/list/del")
def list_del():
    keys = get_user_key()
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
    keys = get_user_key()
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
        return render_template("search_results.html", results=results, query=request.args.get('query'))
    else:
        return redirect(url_for("index"))


@app.route('/follow/<id>')
def follow(id):
    keys = get_user_key()
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
    keys = get_user_key()
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
