
from flask import Flask, render_template, request, redirect, url_for
import requests
import psycopg2
from datetime import datetime

app = Flask("SendEmail")

@app.route("/")
def complaints_form():
    return render_template("trial.html")


@app.route("/thankyou", methods=["POST"]) #can define only one function for one route. if I need multiple functions to take place, I need to define one function uassociated with the route which calls all other functions
#try defining the same route twice and associated with different functions. It's not good practice to usually do this though
def thank_you():
    form_data = request.form
    add_data()
    send_simple_message(form_data["flat"], form_data["name"], form_data["comment"], form_data["email"]) #the order of definition doesn't matter. This is because, here, I'm not calling the function send_simple_message until I go to /thankyou
    return render_template("thankyou.html", data=form_data)

def send_simple_message(flat, name, complaint, email):
    return requests.post(
        "enter API base url/messages",
        auth=("api", "enter an api_key"),
        data={"from": "Admin <enter an email id>",
              "to": email,
              "subject": "Your Complaint Summary",
              "text": "Hi {}, we've received the complaint {} for flat {}".format(name, complaint, flat)})

def add_data():
    form_data = request.form
    conn_string = "host = 'host_name' dbname = 'database_name' user='username' password='password'"
    conn = psycopg2.connect(conn_string)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO complaints (flat, name, comment, created, resolved) VALUES ('{}','{}', '{}', '{}', '{}')".format(form_data["flat"], form_data["name"], form_data["comment"], str(datetime.now()), False))
    conn.commit()
    conn.close()


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


@app.route("/login")
def login_form():
    return render_template("/login.html")


@app.route("/flat", methods = ["POST"])
def login_true():
    login_data = request.form
    user_info = check_login(login_data["username"], login_data["password"])
    if user_info == False:
        return redirect(url_for("login_false"))
    else:
        return render_template ("/flat_homepage.html", user_data = user_info)

def check_login(username, password):
    conn_string = "host = 'host_name' dbname = 'database_name' user='username' password='password'"
    conn = psycopg2.connect(conn_string)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    username_records = cursor.fetchall()
    for row in username_records:
        if row[0] == username and row[1] == password:
            return row
        else:
            continue
    return False


@app.route("/session")
def login_false():
    return render_template("/wrong_login.html")

app.run(debug = True)
