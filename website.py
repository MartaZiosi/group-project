from flask import Flask, render_template, request, redirect, url_for, session
import requests
import psycopg2
import os
from datetime import datetime

app = Flask("SendEmail")
app.secret_key = os.urandom(12)


@app.route("/")
def complaints_form():
    return render_template("index.html")
#Opens to the home page conatining links to all other pages


@app.route("/complaints", methods=["GET"])
def show_complaints():
    conn_string = "host = 'host_name' dbname = 'database_name' user='username' password='password'"
    conn = psycopg2.connect(conn_string)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM complaints")
    records = cursor.fetchall()
    for row in records:
        i = records.index(row)
        dmyt_format_time = row[3].strftime('%b %d, %Y at %H:%M')
        row = row[:3] + (dmyt_format_time, ) + row[4:]
        records[i] = row
    return render_template("complaints.html", records_list = records)
#Open page to register and view all other complaints


@app.route("/thankyou", methods=["POST"])
def thank_you():
    form_data = request.form
    add_data()
    send_simple_message(form_data["flat"], form_data["name"], form_data["comment"], form_data["email"])
    return render_template("thankyou.html", data=form_data)
#Open page summarizing the submitted complaint

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
    cursor.execute("INSERT INTO complaints (flat, name, comment, created, resolved) VALUES ('{}','{}', '{}', '{}', '{}')".format(form_data["flat"], form_data["name"], form_data["comment"], str(datetime.now()), False))
    conn.commit()
    conn.close()
#This function create a new row of values in the table of complaints


@app.route("/login")
def login_form():
    return render_template("/login.html")
#Opens login page


@app.route("/flat", methods = ["POST"])
def login_true():
    login_data = request.form
    check_login(login_data["username"], login_data["password"])
    # user_info = check_login(login_data["username"], login_data["password"])
    if session["logged_in"] == False:
        return redirect(url_for("login_false"))
    elif session["user"] == "admin":
        return redirect(url_for("admin_page"))
    else:
        user_complaints = show_selected_complaints(session["user"])
        return render_template ("/flat_homepage.html", data = user_complaints)
#Opens flat homepage showing all registered complaints by the user if login successful or redirects to login_false function if login unsuccessful

def check_login(username, password):
    conn_string = "host = 'host_name' dbname = 'database_name' user='username' password='password'"
    conn = psycopg2.connect(conn_string)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    username_records = cursor.fetchall()
    for row in username_records:
        if row[0] == username and row[1] == password:
            session["logged_in"] = True
            session["user"] = row[0]
            return True
        else:
            continue
    session["logged_in"] = False
    session["user"] = None
    return False
#This function checks if user entered correct login information


@app.route("/session")
def login_false():
    return render_template("/wrong_login.html")
#Opens the login unsuccessful page giving users the chance to try again


@app.route("/admin")
def admin_page():
    records = show_selected_complaints('admin')
    return render_template("/admin.html", data = records)


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

    for row in records:
        i = records.index(row)
        dmyt_format_time = row[3].strftime('%b %d, %Y at %H:%M')
        row = row[:3] + (dmyt_format_time, ) + row[4:]
        records[i] = row
    return records


app.run(debug = True)
