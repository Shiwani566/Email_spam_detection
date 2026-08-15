from flask import Flask, render_template, request
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
    return render_template("index.html")


# =========================
# PREDICTION ROUTE
# =========================

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


# =========================
# RUN FLASK APP
# =========================

if __name__ == "__main__":
    app.run(debug=True)