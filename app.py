from flask import Flask, render_template, request, url_for, redirect, make_response

from requester import Requester

app = Flask(__name__)

requester = Requester()


def get_user_key():
    if "user_id" in request.cookies.keys() and "user_key" in request.cookies.keys():
        user_id = int(request.cookies.get("user_id"))
        user_key = request.cookies.get("user_key")
        return user_id, user_key
    return None


@app.route("/")
def index():
    if get_user_key():
        return redirect(url_for("lists_menu"))
    else:
        return redirect(url_for("login"))


@app.route("/user")
def user_app():
    return render_template("user.html")


@app.route("/user/register", methods=["GET", "POST"])
def register():
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
