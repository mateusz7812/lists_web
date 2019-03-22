from flask import Flask, render_template, request, url_for, redirect

from requester import Requester

app = Flask(__name__)

requester = Requester()


@app.route("/")
def index():
    return render_template('index.html')


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
    if request.method == "POST":
        requester.make_request(
            {"object": "user", "action": "login",
             "login": request.form["login"],
             "password": request.form["password"]})
        return redirect(url_for("index"))
    return render_template("login.html")

