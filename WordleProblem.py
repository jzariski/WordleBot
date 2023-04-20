import numpy as np
import random
import WordleAgent

def get_dict():
    dictionary = open('wordle_dictionary.txt', 'r')
    dictSet = set()
    for item in dictionary:
        dictSet.add(str(item)[0:len(item) - 1])  
    dictSet.discard('zona')
    dictSet.add('zonal')  
    return dictSet

class WordleProblem():

    def __init__(self):
        self.original_dictionary = get_dict()
        self.dict_as_list = list(self.original_dictionary.copy())
        self.answer = random.choice(self.dict_as_list)

    def isCorrect(self, guess):
        return guess == self.answer
    
    def get_information(self, guess):
        if self.isCorrect(guess):
            print(guess + ' is the correct answer!')
        else:
            green_tuples, yellow_tuples, grey_letters = set(), set(), set()
            for i in range(5):
                if guess[i] == self.answer[i]:
                    green_tuples.add((guess[i], i))
                elif guess[i] in self.answer:
                    yellow_tuples.add((guess[i], i))
                else:
                    grey_letters.add(guess[i])
        return green_tuples, yellow_tuples, grey_letters

prob = WordleProblem()
agent = WordleAgent.WordleAgent()

agent.problem_interface_not_human(prob)
