from flask import Flask, render_template, request
import pickle
import imaplib
import email
from email.header import decode_header



# CREATE FLASK APP


app = Flask(__name__)



# LOAD ML MODEL


with open("model/spam_model.pkl", "rb") as file:
    model = pickle.load(file)



# LOAD VECTORIZER


with open("model/vectorizer.pkl", "rb") as file:
    vectorizer = pickle.load(file)



# HOME PAGE


@app.route("/")
def home():
    return render_template("index.html")



# MANUAL MESSAGE PREDICTION

@app.route("/predict", methods=["POST"])
def predict():

    message = request.form.get("message", "")

    if not message:
        return "Please enter a message."

    message_vectorized = vectorizer.transform([message])

    prediction = model.predict(message_vectorized)[0]

    if prediction == 1:
        result = "SPAM"
    else:
        result = "NOT SPAM"

    return result



# DECODE SUBJECT


def get_subject(msg):

    subject = msg.get("Subject", "")

    try:

        decoded_parts = decode_header(subject)

        final_subject = ""

        for part, encoding in decoded_parts:

            if isinstance(part, bytes):

                if encoding:
                    part = part.decode(
                        encoding,
                        errors="ignore"
                    )
                else:
                    part = part.decode(
                        "utf-8",
                        errors="ignore"
                    )

            final_subject += str(part)

        return final_subject

    except Exception:

        return str(subject)



# GET EMAIL BODY


def get_body(msg):

    body = ""

    try:

        if msg.is_multipart():

            for part in msg.walk():

                content_type = part.get_content_type()

                content_disposition = str(
                    part.get("Content-Disposition", "")
                )

                # Ignore attachments
                if "attachment" in content_disposition.lower():
                    continue

                if content_type == "text/plain":

                    payload = part.get_payload(
                        decode=True
                    )

                    if payload:

                        charset = part.get_content_charset()

                        if charset:

                            body = payload.decode(
                                charset,
                                errors="ignore"
                            )

                        else:

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

                charset = msg.get_content_charset()

                if charset:

                    body = payload.decode(
                        charset,
                        errors="ignore"
                    )

                else:

                    body = payload.decode(
                        "utf-8",
                        errors="ignore"
                    )

    except Exception:

        body = ""

    return body



# FETCH MULTIPLE EMAILS


def fetch_emails(
    email_address,
    app_password,
    email_count
):

    mail = imaplib.IMAP4_SSL(
        "imap.gmail.com"
    )

    results = []

    try:

        
        # LOGIN
        

        mail.login(
            email_address,
            app_password
        )


        
        # OPEN INBOX
        

        status, _ = mail.select("INBOX")

        if status != "OK":
            return []


        
        # GET EMAIL IDS
        

        status, messages = mail.search(
            None,
            "ALL"
        )

        if status != "OK":
            return []


        email_ids = messages[0].split()

        if not email_ids:
            return []


        
        # GET LATEST N EMAILS
        

        latest_ids = email_ids[-email_count:]

        # Newest email first
        latest_ids = latest_ids[::-1]


        
        # PROCESS EACH EMAIL
        

        for email_id in latest_ids:

            try:

                status, msg_data = mail.fetch(
                    email_id,
                    "(RFC822)"
                )

                if status != "OK":
                    continue


                
                # FIND EMAIL DATA
                

                raw_email = None

                for item in msg_data:

                    if isinstance(item, tuple):

                        raw_email = item[1]

                        break


                if not raw_email:
                    continue


                
                # CREATE EMAIL OBJECT
                

                msg = email.message_from_bytes(
                    raw_email
                )


                
                # SUBJECT
                

                subject = get_subject(msg)


                
                # BODY
                

                body = get_body(msg)


                
                # COMBINE SUBJECT + BODY
                

                email_text = (
                    subject + " " + body
                )


                
                # ML PREDICTION
                

                email_vectorized = vectorizer.transform(
                    [email_text]
                )

                prediction = model.predict(
                    email_vectorized
                )[0]


                if prediction == 1:

                    result = "SPAM"

                else:

                    result = "NOT SPAM"


                
                # SAVE RESULT
                

                results.append({

                    "subject": subject,

                    "body": body,

                    "result": result

                })


            except Exception as error:

                # If one email has a problem,
                # continue with the next email.

                print(
                    "Skipped email:",
                    error
                )

                continue


        return results


    finally:

        try:

            mail.logout()

        except Exception:

            pass



# CHECK GMAIL


@app.route(
    "/check-gmail",
    methods=["POST"]
)
def check_gmail():

    
    # GET USER INPUT
    

    email_address = request.form.get(
        "email_address",
        ""
    ).strip()

    app_password = request.form.get(
        "app_password",
        ""
    ).strip()

    email_count = request.form.get(
        "email_count",
        "5"
    )


    
    # VALIDATE INPUT
   

    if not email_address:

        return """
        <h2>Gmail Address Missing</h2>
        <p>Please enter your Gmail address.</p>
        <a href="/">Go Back</a>
        """


    if not app_password:

        return """
        <h2>App Password Missing</h2>
        <p>Please enter your Gmail App Password.</p>
        <a href="/">Go Back</a>
        """


    
    # CONVERT EMAIL COUNT
    

    try:

        email_count = int(
            email_count
        )

    except ValueError:

        email_count = 5


    
    # ALLOWED OPTIONS
    

    allowed_counts = [
        5,
        10,
        15,
        20
    ]


    if email_count not in allowed_counts:

        email_count = 5


    
    # FETCH EMAILS
    

    try:

        emails = fetch_emails(
            email_address,
            app_password,
            email_count
        )


    except imaplib.IMAP4.error:

        return """
        <h2>Gmail Login Failed</h2>

        <p>
        Please check your Gmail address
        and App Password.
        </p>

        <p>
        Make sure IMAP access is available
        for your Gmail account.
        </p>

        <a href="/">Go Back</a>
        """


    except Exception as error:

        print(
            "Gmail error:",
            error
        )

        return """
        <h2>Something went wrong</h2>

        <p>
        We could not fetch the emails.
        </p>

        <a href="/">Go Back</a>
        """


    
    # NO EMAILS
    

    if not emails:

        return """
        <h2>No Emails Found</h2>

        <p>
        No readable emails were found
        in your inbox.
        </p>

        <a href="/">Go Back</a>
        """


   
    # SHOW RESULTS
   

    return render_template(
        "result.html",
        emails=emails
    )


# RUN APPLICATION


if __name__ == "__main__":

    app.run(
        debug=True
    )