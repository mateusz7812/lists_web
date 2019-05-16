from flask import Flask, render_template, request, url_for, redirect, make_response

from requester import Requester

app = Flask(__name__)

requester = Requester()


def get_user_key():
    if ["user_id", "user_key"] in request.cookies.keys():
        user_id = request.cookies.get("user_id")
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
            {"object": "user", "action": "reg",
             "nick": request.form["nick"],
             "login": request.form["login"],
             "password": request.form["password"]})
        if response["info"] == "user added":
            return redirect(url_for("login"))
        return render_template('register.html', info=response["info"])
    return render_template('register.html')


@app.route("/user/login", methods=["GET", "POST"])
def login():
    if get_user_key():
        return redirect(url_for("index"))

    if request.method == "POST":
        db_request = requester.make_request(
            {"object": "user", "action": "login",
             "login": request.form["login"],
             "password": request.form["password"]})
        if db_request["info"] == "session added":
            response = render_template("login.html")
            response.set_cookie(bytes('user_id', "utf-8"), bytes(str(db_request["user_id"]), "utf-8"))
            response.set_cookie('user_key', db_request["user_key"])
            return response
        else:
            return render_template("login.html", error=db_request["info"])

    return render_template("login.html")


@app.route("/list")
def lists_menu():
    keys = get_user_key()
    if keys:
        user_id, user_key = keys
        db_request = requester.make_request(
            {"object": "list", "action": "get",
             "user_id": user_id, "user_key": user_key})
        if db_request["info"] == "lists gotten":
            return render_template("lists_menu.html", lists=db_request["lists"])
        else:
            return render_template("lists_menu.html", error=db_request["info"])
    else:
        return redirect(url_for("index"))



