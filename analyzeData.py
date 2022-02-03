import re
from pickle import load
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

import nltk
nltk.download('stopwords')
nltk.download('punkt')

with open("selected-meals.pickle", "rb") as f:
    selectedMeals = load(f)
with open("unselected-meals.pickle", "rb") as f:
    unselectedMeals = load(f)

englishStopwords = stopwords.words('english')
frenchStopwords = stopwords.words('french')
allStopwords = englishStopwords + frenchStopwords

def preprocess(meal):
    # Convert to lowercase
    meal = meal.lower()
    # Remove punctuation
    meal = re.sub(r'[^\w\s]', '', meal)
    # Tokenize
    meal = word_tokenize(meal)
    # Remove stopwords
    meal = [token for token in meal if token not in allStopwords]

    return meal

[preprocess(meal) for meal in selectedMeals]
[preprocess(meal) for meal in unselectedMeals]