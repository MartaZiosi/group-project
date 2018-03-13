from flask import Flask, render_template, request, redirect, url_for, session
import requests
import psycopg2
# import os
from datetime import datetime

app = Flask("SendEmail")
# app.secret_key = os.urandom(12)
app.secret_key = "add_a_secret_key"#need a fixed key as using the random one doesn't work with Heroku(a new random key is generated for each request)


@app.route("/")
def complaints_form():
    return render_template("index.html")
#Opens to the home page conatining links to all other pages


@app.route("/about")
def about():
    return render_template("about.html")



@app.route("/announcements")
def announcement():
    conn_string = "host = 'host_name' dbname = 'database_name' user='username' password='password'"
    conn = psycopg2.connect(conn_string)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM announcements ORDER BY posted DESC")
    records = cursor.fetchall()
    conn.close()
    for row in records:
        i = records.index(row)
        dmyt_format_time = row[2].strftime('%b %d, %Y at %H:%M')
        row = row[:2] + (dmyt_format_time, )
        records[i] = row
    return render_template("announcements.html", records_list = records)



@app.route("/thankyou", methods=["POST"])
def thank_you():
    add_data()
    return redirect("/user")
#redirect to user complaints page

def send_simple_message(flat, name, complaint, email):
    return requests.post(
        "enter API base url/messages",
        auth=("api", "enter an api_key"),
        data={"from": "Admin <enter an email id>",
              "to": email,
              "subject": "Your Complaint Summary",
              "text": "Hi {}, we've received the complaint {} for flat {}".format(name, complaint, flat)})
#This function sends an email summarizing the submitted complaint to the email provided

def add_data():
    form_data = request.form
    conn_string = "host = 'host_name' dbname = 'database_name' user='username' password='password'"
    conn = psycopg2.connect(conn_string)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO complaints (flat, name, comment, created, resolved) VALUES ('{}','{}', '{}', '{}', '{}')".format(session["user"], form_data["name"], form_data["comment"], str(datetime.now()), False))
    conn.commit()
    conn.close()
#This function create a new row of values in the table of complaints


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        session.pop("user", None)
        login_data = request.form
        if check_login(login_data["username"], login_data["password"]):
            session["user"] = login_data["username"]
            return redirect(url_for("homepage"))
        else:
            return render_template("wrong_login.html")
    return render_template("login.html")


def check_login(username, password):
    conn_string = "host = 'host_name' dbname = 'database_name' user='username' password='password'"
    conn = psycopg2.connect(conn_string)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    username_records = cursor.fetchall()
    for row in username_records:
        if row[0] == username and row[1] == password:
            return True
        else:
            continue
    return False



@app.route("/user")
def homepage():
    if "user" in session:
        if session["user"] == "admin":
            all_complaints = show_selected_complaints('admin')
            return render_template("admin.html", data = all_complaints)
        else:
            user_complaints = show_selected_complaints(session["user"])
            return render_template ("flat_homepage.html", data = user_complaints)
    return redirect(url_for("login"))


def show_selected_complaints(username):
    conn_string = "host = 'host_name' dbname = 'database_name' user='username' password='password'"
    conn = psycopg2.connect(conn_string)
    cursor = conn.cursor()
    if username == "admin":
        cursor.execute("SELECT * FROM complaints ORDER BY created DESC")
        records = cursor.fetchall()
    else:
        cursor.execute("SELECT * FROM complaints WHERE flat = '{}' ORDER BY created DESC".format(username))
        records = cursor.fetchall()
    conn.close()

    for row in records:
        i = records.index(row)
        dmyt_format_time = row[3].strftime('%b %d, %Y at %H:%M')
        row = row[:3] + (dmyt_format_time, ) + row[4:]
        records[i] = row
    return records



@app.route("/user/confirming-submission", methods=["POST"])
def update_complaints():
    conn_string = "host = 'host_name' dbname = 'database_name' user='username' password='password'"
    conn = psycopg2.connect(conn_string)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM complaints")
    records = cursor.fetchall()
    for row in records:
        checkbox_name = "resolved_check_comment_{}".format(row[0])
        if request.form.get(checkbox_name):
            # return "Updated {}".format(checkbox_name)
            cursor.execute("UPDATE complaints SET resolved = True WHERE id = '{}'".format(row[0]))
            conn.commit()
        else:
            cursor.execute("UPDATE complaints SET resolved = False WHERE id = '{}'".format(row[0]))
            conn.commit()
    conn.close()
    return redirect("/user")



@app.route("/signout")
def sign_out():
    session.pop("user", None)
    return redirect(url_for("login"))



@app.route("/user/account-info")
def account_info():
    return render_template("account_info.html")



@app.route("/user/change-account-info", methods = ["POST"])
def change_info():
    records = request.form
    if change_password(records["old-password"], records["new-password"]):
        session.pop("user", None)
        return render_template("successful_change.html")
    else:
        return render_template("unsuccessful_change.html")


def change_password(old_password, new_password):
    conn_string = "host = 'host_name' dbname = 'database_name' user='username' password='password'"
    conn = psycopg2.connect(conn_string)
    cursor = conn.cursor()
    # username = session["user"]
    cursor.execute("SELECT password FROM users WHERE username = '{}'".format(session["user"]))
    records = cursor.fetchall()
    if records[0][0] == old_password:
        cursor.execute("UPDATE users SET password = '{}' WHERE username = '{}'".format(new_password, session["user"]))
        conn.commit()
        conn.close()
        return True
    else:
        conn.close()
        return False


app.run(debug = True)
