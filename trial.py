# from flask import Flask, render_template, request
#
# app = Flask("MyApp")
#
# @app.route("/")
# def hello():
#     return "Hello world!"
#
# if __name__ == "__main__":
#     app.run(debug = True)
from flask import Flask, render_template, request
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
    main()
    #main(form_data["flat"], form_data["name"], form_data["comment"])
    send_simple_message(form_data["flat"], form_data["name"], form_data["comment"], form_data["email"]) #the order of definition doesn't matter. This is because, here, I'm not calling the function send_simple_message until I go to /thankyou
    return render_template("thankyou.html", data=form_data)

def send_simple_message(flat, name, complaint, email):
    return requests.post(
        "***REMOVED***/messages",
        auth=("api", "***REMOVED***"),
        data={"from": "Admin <***REMOVED***>",
              "to": email,
              "subject": "Your Complaint Summary",
              "text": "Hi {}, we've received the complaint {} for flat {}".format(name, complaint, flat)})


def main():
    form_data = request.form
    # na=form_data["name"]
    # fl=form_data["flat"]
    # com=form_data["comment"]
    #time = datetime.now()
    conn_string = "host = 'localhost' dbname = 'tenants' user='postgres' password='***REMOVED***'"
    conn = psycopg2.connect(conn_string)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO complaints (flat, name, comment, created, resolved) VALUES ('{}','{}', '{}', '{}', '{}')".format(form_data["flat"], form_data["name"], form_data["comment"], str(datetime.now()), False))
    conn.commit()

    #cursor.close()
    conn.close()

    #
#     records = cursor.fetchall()
#     #print(records)
#     for number in range(len(records[0])):
#         print(records[0][number])
#
# if __name__ == "__main__":
#     main()

app.run(debug = True)

#
# import psycopg2
#
# def main():
#     conn_string = "host = 'localhost' dbname = 'tenants' user='postgres' password='***REMOVED***'"
#     conn = psycopg2.connect(conn_string)
#     cursor = conn.cursor()
#     cursor.execute("SELECT flat, name, comment, created, resolved FROM complaints")
#     records = cursor.fetchall()
#     #print(records)
#     for number in range(len(records[0])):
#         print(records[0][number])
#
# if __name__ == "__main__":
#     main()
