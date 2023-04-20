import numpy as np
import random

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
        newDict = self.current_dictionary.copy()
        for item in self.current_dictionary:
            for tup in self.green_tuples:
                letter, index = tup[0], tup[1]
                if item[index] != letter:
                    newDict.discard(item)
            
            for tup in self.yellow_tuples:
                letter, index = tup[0], tup[1]
                if letter not in item:
                    newDict.discard(item)

            for letter in self.grey_letters:
                if letter in item:
                    newDict.discard(item)
        newDict.discard(guess)
        self.current_dictionary= newDict


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
        guess = self.make_guess_random()
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
    