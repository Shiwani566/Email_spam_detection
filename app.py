from flask import Flask, render_template, request
from dotenv import load_dotenv
import pickle
import os
import imaplib
import email
from email.header import decode_header



# LOAD ENVIRONMENT VARIABLES


load_dotenv()

EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_APP_PASSWORD = os.getenv("EMAIL_APP_PASSWORD")


# CREATE FLASK APP


app = Flask(__name__)



# LOAD TRAINED MODEL


with open("model/spam_model.pkl", "rb") as file:
    model = pickle.load(file)


# LOAD VECTORIZER


with open("model/vectorizer.pkl", "rb") as file:
    vectorizer = pickle.load(file)



# HOME ROUTE


@app.route("/")
def home():
    return render_template("index.html")



# MANUAL PREDICTION ROUTE


@app.route("/predict", methods=["POST"])
def predict():

    message = request.form["message"]

    message_vectorized = vectorizer.transform([message])

    prediction = model.predict(message_vectorized)[0]

    if prediction == 1:
        result = "SPAM"
    else:
        result = "NOT SPAM"

    return result



# CONNECT TO GMAIL


def connect_to_gmail():

    mail = imaplib.IMAP4_SSL("imap.gmail.com")

    mail.login(
        EMAIL_ADDRESS,
        EMAIL_APP_PASSWORD
    )

    return mail



# FETCH LATEST EMAIL


def fetch_latest_email():

    mail = connect_to_gmail()

    mail.select("INBOX")

    status, messages = mail.search(None, "ALL")

    if status != "OK":
        mail.logout()
        return None

    email_ids = messages[0].split()

    if not email_ids:
        mail.logout()
        return None

    latest_email_id = email_ids[-1]

    status, msg_data = mail.fetch(
        latest_email_id,
        "(RFC822)"
    )

    if status != "OK":
        mail.logout()
        return None

    raw_email = msg_data[0][1]

    msg = email.message_from_bytes(raw_email)


    
    # GET SUBJECT
   

    subject, encoding = decode_header(
        msg.get("Subject", "")
    )[0]

    if isinstance(subject, bytes):

        if encoding:
            subject = subject.decode(
                encoding,
                errors="ignore"
            )
        else:
            subject = subject.decode(
                "utf-8",
                errors="ignore"
            )


    # GET EMAIL BODY
   

    body = ""

    if msg.is_multipart():

        for part in msg.walk():

            content_type = part.get_content_type()

            content_disposition = str(
                part.get("Content-Disposition")
            )

            if (
                content_type == "text/plain"
                and "attachment" not in content_disposition
            ):

                payload = part.get_payload(
                    decode=True
                )

                if payload:
                    body = payload.decode(
                        "utf-8",
                        errors="ignore"
                    )

                break

    else:

        payload = msg.get_payload(
            decode=True
        )

        if payload:
            body = payload.decode(
                "utf-8",
                errors="ignore"
            )


    mail.logout()

    return {
        "subject": subject,
        "body": body
    }



# FETCH EMAIL ROUTE


@app.route("/fetch-email")
def fetch_email():

    email_data = fetch_latest_email()

    if email_data is None:
        return "No email found."

    return {
        "subject": email_data["subject"],
        "body": email_data["body"]
    }



# RUN FLASK APP


if __name__ == "__main__":
    app.run(debug=True)