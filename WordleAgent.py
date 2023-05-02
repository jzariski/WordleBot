import numpy as np
import random
from sklearn import linear_model
import random
#from xgboost import XGBRegressor
def get_dict():
    dictionary = open('wordle_dictionary.txt', 'r')
    dictSet = set()
    for item in dictionary:
        dictSet.add(str(item)[0:len(item) - 1]) 
    dictSet.discard('zona')
    dictSet.add('zonal')   
    return dictSet

def get_letter_count(wordSet):
    letter_count = dict()
    for word in wordSet:
        for letter in word:
            if letter not in letter_count.keys():
                letter_count[letter] = 1
            else:
                letter_count[letter] = letter_count[letter] + 1
    return letter_count

def train_regress(prob):
    dictionary = dict()

    for i in range(10000):
        #print('Training Step ', i)
        agent = WordleAgent()

        pairs = agent.problem_interface_get_info(prob)

        for item in pairs:
            string, discards = item[0], item[1]
            if string not in dictionary.keys():
                dictionary[string] = []
            dictionary[string].append(discards)

    X = []
    Y = []
    for string in dictionary.keys():
        dictionary[string] = np.mean(dictionary[string])
        X.append(agent.encodeWord(string))
        Y.append(dictionary[string])
    X = np.asarray(X)
    Y = np.asarray(Y)

    regr = linear_model.LinearRegression()
    #regr = XGBRegressor()
    regr.fit(X, Y)
    return regr    

class WordleAgent():

    def __init__(self):
        self.original_dictionary = get_dict()
        self.current_dictionary = self.original_dictionary.copy()
        self.green_tuples = set()
        self.yellow_tuples = set()
        self.grey_letters = set()

    
    def augment_information(self, tuples):
        greens, yellows, greys = tuples
        for green in greens:
            self.green_tuples.add(green)
        for yellow in yellows:
            self.yellow_tuples.add(yellow)
        for grey in greys:
            self.grey_letters.add(grey)
        
    def augment_possible_answers(self, guess):
        total = len(self.current_dictionary)
        newDict = self.current_dictionary.copy()
        for item in self.current_dictionary:
            remove = False
            val = 0
            for tup in self.green_tuples:
                letter, index = tup[0], tup[1]
                if item[index] != letter:
                    remove = True
                    val += 2
            
            for tup in self.yellow_tuples:
                letter, index = tup[0], tup[1]
                if letter not in item:
                    remove = True
                    val += 5

            for letter in self.grey_letters:
                if letter in item:
                    newDict.discard(item)
                    remove = True
                    val += 10

            if remove:
                newDict.discard(item)
        newDict.discard(guess)
        self.current_dictionary= newDict
        return val * (1-(total/len(self.original_dictionary)))


    ## These guess functions only choose from a space of possible answers
    ## Could limit the amount of new information that can be obtained

    def make_guess_random(self):
        guess_list = list(self.current_dictionary.copy())
        return random.choice(guess_list)
    
    def make_guess_choice(self):
        totalLetters = 5 * len(self.original_dictionary)
        max, maxWord = -1 * np.inf, None
        letter_count = get_letter_count(self.current_dictionary)
        for word in self.current_dictionary:
            word_score = 0
            for letter in word:
                word_score += letter_count[letter] / totalLetters
            if word_score > max:
                max = word_score
                maxWord = word
        return maxWord


    def problem_interface_not_human(self, wordleProblem):
        print('Welcome to WordleBot')
        #guess = self.make_guess_random()
        guess = self.make_guess_choice()
        guessCount = 1
        while not wordleProblem.isCorrect(guess):
            print('Guess: ', guess)
            tuples = wordleProblem.get_information(guess)
            self.augment_information(tuples)
            self.augment_possible_answers(guess)
            guess = self.make_guess_random()
            guessCount += 1
        print('Guess: ', guess)
        print(guess, ' is correct!')
        print('Solved in ', guessCount, ' guesses!')
        return guessCount
    
    def problem_interface_no_print(self, wordleProblem):
        guess = self.make_guess_random()
        guessCount = 1
        while not wordleProblem.isCorrect(guess):
            tuples = wordleProblem.get_information(guess)
            self.augment_information(tuples)
            self.augment_possible_answers(guess)
            guess = self.make_guess_random()
            guessCount += 1
        return guessCount
    
    def encodeWord(self, guess):
        arrays = np.zeros(1)
        alphabet = 'abcdefghijklmnopqrstuvwxyz'
        for letter in guess:
            letter_num = alphabet.index(letter)
            one_hot = np.zeros(26)
            one_hot[letter_num] = 1
            arrays = np.concatenate((arrays, one_hot), axis =0)
        return arrays


    
    def problem_interface_get_info(self, wordleProblem):
        #print('Welcome to WordleBot')
        guess = self.make_guess_random()
        guessCount = 1
        tups = set()
        while not wordleProblem.isCorrect(guess):
            #print('Guess: ', guess)
            tuples = wordleProblem.get_information(guess)
            self.augment_information(tuples)
            discards = self.augment_possible_answers(guess)
            guess = self.make_guess_random()
            guessCount += 1
            tups.add((guess, discards))
        #print('Guess: ', guess)
        #print(guess, ' is correct!')
        #print('Solved in ', guessCount, ' guesses!')
        return tups
    
    def make_guess_regress(self, regr):
        guess, score = None, -1*np.inf
        for item in self.current_dictionary:
            word = self.encodeWord(item).reshape(1,-1)
            newScore = regr.predict(word)
            if newScore > score:
                guess = item
                score = newScore
        return guess

    def problem_interface_regress(self, wordleProblem, regr):        
        guess = self.make_guess_regress(regr)
       
        guessCount = 1
        while not wordleProblem.isCorrect(guess):
            tuples = wordleProblem.get_information(guess)
            self.augment_information(tuples)
            self.augment_possible_answers(guess)
            num = random.random()
            if num > 0.4:
                guess = self.make_guess_regress(regr)
            else:
                guess = self.make_guess_random()
            guessCount += 1
        return guessCount
