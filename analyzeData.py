import re
import pandas as pd
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

selectedMeals = [preprocess(meal) for meal in selectedMeals]
unselectedMeals = [preprocess(meal) for meal in unselectedMeals]

# Convert meals to a list of words. 
selected = pd.Series([word for meal in selectedMeals for word in meal])
unselected = pd.Series([word for meal in unselectedMeals for word in meal])

# Count the appearances of each word. 
selectedCounts = selected.value_counts()
unselectedCounts = unselected.value_counts()
selectedLength = len(selected)
unselectedLength = len(unselected)

# Get the frequency of the appearance of word as a 
# percentage of the total number of words. 
def getWordFreqPercentage(word, vocabCounts, vocabLength):
    try:
        return vocabCounts[word] / vocabLength
    except KeyError:
        return 0

# Use the word frequency percentage to rank the meals for 
# the upcoming week. 
with open("upcoming-meals.pickle", "rb") as f:
    upcomingMeals = load(f)

# Preprocess upcoming meals. 
upcomingMeals = [(meal, preprocess(meal)) for meal in upcomingMeals]

def computeScore(meal):
    selectedScore = sum([getWordFreqPercentage(word, selectedCounts, selectedLength) for word in meal])
    unselectedScore = sum([getWordFreqPercentage(word, unselectedCounts, unselectedLength) for word in meal])
    return selectedScore - unselectedScore

scores = [(mealName, computeScore(processedMealName)) for mealName, processedMealName in upcomingMeals]
scores.sort(key=lambda score: score[1], reverse=True)
print(scores)