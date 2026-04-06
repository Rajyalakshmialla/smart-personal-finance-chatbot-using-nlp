import joblib

# Load trained model and vectorizer
model = joblib.load("nlp_model.pkl")
vectorizer = joblib.load("vectorizer.pkl")

def get_intent(text):
    """
    Input: text (str) - user query
    Output: predicted intent (str)
    """
    vec = vectorizer.transform([text])
    return model.predict(vec)[0]

# Optional test
if __name__ == "__main__":
    while True:
        query = input("You: ")
        if query.lower() in ["exit", "quit"]:
            break
        print("Predicted Intent:", get_intent(query))
