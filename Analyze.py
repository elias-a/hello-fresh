import os
import re
import nltk
import pandas as pd
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

class Analyze:
    def __init__(self):
        self._stopwords = []

    def preprocess(self, meal):
        # Convert to lowercase
        meal = meal.lower()
        # Remove punctuation
        meal = re.sub(r"[^\w\s]", "", meal)
        # Tokenize
        meal = word_tokenize(meal)
        # Remove stopwords
        meal = [token for token in meal if token not in self._stopwords]

        return meal

    # Get the frequency of the appearance of word as a 
    # percentage of the total number of words. 
    @staticmethod
    def getWordFreqPercentage(word, vocabCounts, vocabLength):
        try:
            return vocabCounts[word] / vocabLength
        except KeyError:
            return 0

    def computeScore(self, meal):
        return sum([
            Analyze.getWordFreqPercentage(word, self._wordCounts, len(self._meals)) 
            for word in meal])

    def selectMeals(self, pastMeals, upcomingMeals):
        downloadDirectory = os.path.join(os.path.dirname(__file__), "nltk_data")
        nltk.download("stopwords", download_dir=downloadDirectory, quiet=True)
        nltk.download("punkt", download_dir=downloadDirectory, quiet=True)
        nltk.data.path.append(downloadDirectory)

        englishStopwords = stopwords.words("english")
        frenchStopwords = stopwords.words("french")
        self._stopwords = englishStopwords + frenchStopwords

        pastMeals = [self.preprocess(meal) for meal in pastMeals]

        # Convert meals to a list of words. 
        self._meals = pd.Series([word for meal in pastMeals for word in meal])
        self._wordCounts = self._meals.value_counts()

        # Use the word frequency percentage to rank the meals for 
        # the upcoming week. 

        # Preprocess upcoming meals. 
        upcomingMeals = [(meal, self.preprocess(meal)) for meal in upcomingMeals]

        scores = [(mealName, self.computeScore(processedMealName)) for mealName, processedMealName in upcomingMeals]
        scores.sort(key=lambda score: score[1], reverse=True)
        return scores

