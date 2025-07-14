import re
import string
import nltk
from nltk.corpus import stopwords, wordnet
from nltk.tokenize import TreebankWordTokenizer
from nltk import pos_tag
from nltk.stem import WordNetLemmatizer
from textblob import Word

# Downloads
nltk.download('punkt')
nltk.download('wordnet')
nltk.download('stopwords')
nltk.download('averaged_perceptron_tagger_eng')

# Initialization
stop_words = set(stopwords.words('english'))
tokenizer = TreebankWordTokenizer()
lemmatizer = WordNetLemmatizer()

# Helper Functions
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
    # Remove HTML tags
    text = re.sub(r'<.*?>', '', text)
    # Remove special characters, keep letters only
    text = re.sub(r'[^a-zA-Z]', ' ', text).lower()
    tokens = tokenizer.tokenize(text)
    # Normalize + remove stopwords
    return ' '.join([normalize_word(t) for t in tokens if t not in stop_words and t not in string.punctuation])
