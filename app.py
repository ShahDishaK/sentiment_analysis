# from fastapi import FastAPI
# from pydantic import BaseModel
# import joblib
# from preprocessing import normalize_review
# from fastapi.middleware.cors import CORSMiddleware
# import spacy

# app = FastAPI()

# # Enable CORS (if frontend is on a different origin)
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],  # Change to your frontend domain in production
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # Load pre-trained model and vectorizer
# model = joblib.load("sentiment_model.pkl")
# vectorizer = joblib.load("tfidf_vectorizer.pkl")

# class Review(BaseModel):
#     text: str
# nlp = spacy.load("en_core_web_sm")

# # @app.post("/predict/")
# # def predict_sentiment(review: Review):
# #     try:
# #         cleaned = normalize_review(review.text)
# #         vectorized = vectorizer.transform([cleaned])
# #         prediction = model.predict(vectorized)[0]
# #         sentiment = "Positive" if prediction == 1 else "Negative"
# #         return {"sentiment": sentiment}
# #     except Exception as e:
# #         return {"error": str(e)}

# def is_negated_positive(doc):
#     negative_lemmas = {
#         "bad", "terrible", "awful", "disgust", "dreadful",
#         "regrettable", "horrible", "failure", "unpleasant", "disappoint"
#     }
    
#     print("Tokens and their dependencies:")
#     for token in doc:
#         print(f"Token: {token.text}, Dep: {token.dep_}, Lemma: {token.lemma_}")

#     # Check for negations like "not bad", "not horrible"
#     for token in doc:
#         if token.dep_ == "neg" and token.head.lemma_.lower() in negative_lemmas:
#             return True

#     # Check for "nothing horrible", "nothing disgusting"
#     for i, token in enumerate(doc[:-1]):
#         if token.text.lower() == "nothing" and doc[i+1].lemma_.lower() in negative_lemmas:
#             return True

#     return False



# @app.post("/predict/")
# def predict_sentiment(review: Review):
#     try:
#         print(f"Received text: {review.text}")
#         doc = nlp(review.text.lower())

#         # Apply negation check first
#         if is_negated_positive(doc):
#             return {"sentiment": "Positive"}

#         # Normalizing review text
#         cleaned = normalize_review(review.text)
#         print(f"Cleaned Review: {cleaned}")
        
#         # Vectorizing the cleaned text
#         vectorized = vectorizer.transform([cleaned])
#         print(f"Vectorized Review: {vectorized}")

#         # Model prediction
#         prediction = model.predict(vectorized)[0]
#         print(f"Prediction: {prediction}")
        
#         # Determine sentiment
#         sentiment = "Positive" if prediction == 1 else "Negative"
        
#         return {"sentiment": sentiment}
    
#     except Exception as e:
#         print(f"Error during prediction: {e}")
#         return {"error": str(e)}
# Final





from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
import re
import nltk
from nltk.tokenize import TreebankWordTokenizer
from nltk.corpus import wordnet
from nltk import pos_tag
from nltk.stem import WordNetLemmatizer
from textblob import Word
import spacy

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Load NLP resources
nltk.download('punkt')
nltk.download('wordnet')
nltk.download('averaged_perceptron_tagger')

# Load Spacy model and ML model/vectorizer
nlp = spacy.load("en_core_web_sm")
model = joblib.load('sentiment_model1.pkl')
vectorizer = joblib.load('tfidf_vectorizer1.pkl')

# Preprocessing functions
tokenizer = TreebankWordTokenizer()
lemmatizer = WordNetLemmatizer()

def reduce_repeated_letters(word):
    return re.sub(r'(.)\1{2,}', r'\1\1', word)

def get_wordnet_pos(treebank_tag):
    if treebank_tag.startswith('J'):
        return wordnet.ADJ
    elif treebank_tag.startswith('V'):
        return wordnet.VERB
    elif treebank_tag.startswith('N'):
        return wordnet.NOUN
    elif treebank_tag.startswith('R'):
        return wordnet.ADV
    else:
        return wordnet.NOUN

def normalize_word(word):
    word = reduce_repeated_letters(word)
    corrected = str(Word(word).correct())
    pos = pos_tag([corrected])[0][1]
    return lemmatizer.lemmatize(corrected, get_wordnet_pos(pos))

def normalize_review(text):
    tokens = tokenizer.tokenize(text)
    normalized_tokens = [normalize_word(token) for token in tokens]
    return ' '.join(normalized_tokens)

def is_negated_positive(doc):
    negative_lemmas = {
        "bad", "terrible", "awful", "disgust", "dreadful",
        "regrettable", "horrible", "failure", "unpleasant", "disappoint"
    }
    for token in doc:
        if token.dep_ == "neg" and token.head.lemma_.lower() in negative_lemmas:
            return True
    for i, token in enumerate(doc[:-1]):
        if token.text.lower() == "nothing" and doc[i+1].lemma_.lower() in negative_lemmas:
            return True
    return False

def predict_sentiment(text):
    doc = nlp(text.lower())
    if is_negated_positive(doc):
        return "Positive"
    cleaned = normalize_review(text)
    vector = vectorizer.transform([cleaned])
    pred = model.predict(vector)[0]
    sentiment_mapping = {0: 'Positive', 1: 'Negative'}
    return sentiment_mapping[pred]

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()
        text = data.get('text', '')
        result = predict_sentiment(text)
        return jsonify({'sentiment': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Only run when directly executing this file
if __name__ == '__main__':
    app.run(port=5000)