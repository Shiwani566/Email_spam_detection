import pandas as pd
import pickle
import os

from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import accuracy_score


# =========================
# 1. LOAD DATASET
# =========================

data = pd.read_csv("dataset/spam.csv", encoding="latin-1")

# Keep only the required columns
data = data[["v1", "v2"]]

# Rename columns
data.columns = ["label", "message"]


# =========================
# 2. CONVERT LABELS
# =========================

# ham = 0
# spam = 1
data["label"] = data["label"].map({
    "ham": 0,
    "spam": 1
})


# =========================
# 3. SPLIT DATA
# =========================

X = data["message"]
y = data["label"]

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)


# =========================
# 4. TEXT VECTORIZATION
# =========================

vectorizer = CountVectorizer()

X_train_vectorized = vectorizer.fit_transform(X_train)
X_test_vectorized = vectorizer.transform(X_test)


# =========================
# 5. TRAIN MODEL
# =========================

model = MultinomialNB()

model.fit(X_train_vectorized, y_train)


# =========================
# 6. TEST MODEL
# =========================

y_pred = model.predict(X_test_vectorized)

accuracy = accuracy_score(y_test, y_pred)

print("Model trained successfully!")
print(f"Accuracy: {accuracy * 100:.2f}%")


# =========================
# 7. CREATE MODEL FOLDER
# =========================

os.makedirs("model", exist_ok=True)


# =========================
# 8. SAVE MODEL
# =========================

with open("model/spam_model.pkl", "wb") as file:
    pickle.dump(model, file)


# =========================
# 9. SAVE VECTORIZER
# =========================

with open("model/vectorizer.pkl", "wb") as file:
    pickle.dump(vectorizer, file)


print("Model saved to: model/spam_model.pkl")
print("Vectorizer saved to: model/vectorizer.pkl")