from flask import Flask
import pickle


# =========================
# CREATE FLASK APP
# =========================

app = Flask(__name__)


# =========================
# LOAD TRAINED MODEL
# =========================

with open("model/spam_model.pkl", "rb") as file:
    model = pickle.load(file)


# =========================
# LOAD VECTORIZER
# =========================

with open("model/vectorizer.pkl", "rb") as file:
    vectorizer = pickle.load(file)


# =========================
# HOME ROUTE
# =========================

@app.route("/")
def home():
    return "Email Spam Detection App is Running!"


# =========================
# PREDICTION ROUTE
# =========================

@app.route("/predict", methods=["POST"])
def predict():

    message = "Congratulations! You have won a free prize!"

    message_vectorized = vectorizer.transform([message])

    prediction = model.predict(message_vectorized)[0]

    if prediction == 1:
        result = "SPAM"
    else:
        result = "NOT SPAM"

    return result


# =========================
# RUN FLASK APP
# =========================

if __name__ == "__main__":
    app.run(debug=True)