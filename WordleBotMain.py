
from csv import writer, reader
from mimetypes import guess_all_extensions
from os import remove
from statistics import correlation
import sys
from datetime import date


Possible_Answers = []
Possible_Answers_Left = []
bestGuesses = []
global correctLetters
debug = False



### better way to score letters/words
###         - Maybe also a longer list of test words
###         - This could just be used to more accurately score letters/words, including words longer than 5 letters

### A way to decide when to introduce words with "letter multiples" (words with the same letter more than once)
###         - Currently I don't introduce letter multiples until at least the third guess, but it's possible before that, in which case the bot returns null


### Improve how we consider past "Green" or "Yellow" letters! Currently the only consideration is if the letter is IN the word, not what it's location in the word is

### take Black letters into account based on position, rather than just if it's in the word


def load_all_possible_answers():
    with open("Answers2.txt", 'r') as file:
        lines = file.readlines()
        for line in lines:
            letters = [letter for letter in line]
            letters = letters[:-1]
            Possible_Answers.append(letters)

def scoreLetters():
    letterScores = {}
    for answer in Possible_Answers:
        for letter in answer:
            if letter not in letterScores.keys():
                letterScores[letter] = 1
            else:
                letterScores[letter] += 1

    return letterScores

def scoreWords(letterscores, GuessNum):
    wordScores = {}
    for answer in Possible_Answers:
        joinAns = "".join(answer)
        for letter in answer:
            if joinAns not in wordScores.keys():
                wordScores[joinAns] = [letterscores[letter],1]
            else:
                wordScores[joinAns][0] += letterscores[letter]
                if joinAns.count(letter) > 1:
                    wordScores[joinAns][1] = 2
    return wordScores


def GetPastCorrectLetters(PastGuessInfo, Sequence, Guess): 
    CorrectLetters = ""
    for row in PastGuessInfo:
        if row[0] == date.today().strftime("%m/%d/%Y"):
            for i in range(len(row[1])):
                if row[1][i] == 'g' or row[1][i] == 'y':
                    CorrectLetters += row[2][i]
    for i in range(len(Sequence)):
        if Sequence[i] == 'g' or Sequence[i] == 'y':
            CorrectLetters += Guess[i]
    return CorrectLetters

def GetPastIncorrectLetters(PastGuessInfo, Sequence, Guess):

    IncorrectLetters = ""
    
    for row in PastGuessInfo:
        if row[0] == date.today().strftime("%m/%d/%Y"):
            for i in range(len(row[1])):
                if row[1][i] == 'b':
                    IncorrectLetters += row[2][i]
    for i in range(len(Sequence)):
        if Sequence[i] == 'b':
            IncorrectLetters += Guess[i]
    return IncorrectLetters


    

def SavePastGuesses(Sequence, Guess, GuessNum, PastCorrectLetters, PastIncorrectLetters):
    today = date.today()
    import_data = [today.strftime("%m/%d/%Y"), Sequence, Guess, GuessNum, PastCorrectLetters, PastIncorrectLetters]

    with open('PastGuessInfo.csv', 'a', newline = '\n') as pgInfo:
        writer_obj = writer(pgInfo)
        writer_obj.writerow(import_data)   
        pgInfo.close() 

def loadPastGuessInfo():
    pastGuessInfo = []
    today = date.today()

    with open('PastGuessInfo.csv', 'r', newline = '\n') as pgInfo:
        read = reader(pgInfo)
        next(read) #just interested in the info, so we skip the header row
        for row in read:
            if row[0] == today.strftime("%m/%d/%Y"): #currently only interested in today's guesses. There may be more analysis possible in the future for optimization
                pastGuessInfo.append(row)
        pgInfo.close()

    return pastGuessInfo


def Possible_Words_Left(PastSequence, CurrentGuess, badLetters, GuessNum, wordScores):
    PS_Letters = list(PastSequence)
    CG_Letters = list(CurrentGuess)
    bLetters = list(badLetters)
    correctLetters = 0
    for i in range(len(PS_Letters)):
        if PS_Letters[i] == 'y' or PS_Letters[i] == 'g':
            correctLetters += 1



    for answer in Possible_Answers:
        yCounter = 0
        gCounter = 0
        goodAnswer = False

        for i in range(len(CG_Letters)):


            if PS_Letters[i] == 'y':
                if CG_Letters[i] in answer and answer[i] != CG_Letters[i] and answer not in Possible_Answers_Left:
                    yCounter += 1
            elif PS_Letters[i] == 'g':
                if CG_Letters[i] in answer and CG_Letters[i] == answer[i] and answer not in Possible_Answers_Left:
                    gCounter += 1

            if yCounter + gCounter == PS_Letters.count('y') + PS_Letters.count('g'):
                goodAnswer = True
        if goodAnswer:
            Possible_Answers_Left.append(answer)



### noted this at the top, but currently I only allow words with multiple of the same letter to 
### be "Guessed" AFTER at least the second guess (third guess is the first one possible)
    wordsToDelete = [key for key in wordScores if wordScores[key][1] == 2 and int(GuessNum) < 2]

    for ans in list(Possible_Answers_Left):
        badAnswer = False
        ans = "".join(ans)
        for letter in bLetters:
            if letter in ans:
                badAnswer = True
            elif ans == CurrentGuess:
                badAnswer = True
            elif int(GuessNum) < 3 and ans in wordsToDelete:     
                # print(letter, ans)
                badAnswer = True
        if badAnswer:
            wordsToDelete.append(ans)
    for word in list(wordsToDelete):
        word = list(word)
        if word in list(Possible_Answers_Left):
            Possible_Answers_Left.remove(word)
    # for ans in Possible_Answers_Left:
    #     print(ans)
    return Possible_Answers_Left



def PickBestWord(Answers_Left, correctLetters, Sequence, Guess, wordScores):
    PS_Letters = list(Sequence)
    CG_Letters = list(Guess)
    guessLetters = {}
    letters = {}
    maxScore = 0
    bestGuess = ""


    for ans in sorted(list(Answers_Left)):
        removeFromAnswers = 0
        if "*" not in correctLetters:
            for letter in correctLetters:
                if letter in ans:
                    removeFromAnswers += 1      
            # for i in range(len(correctLetters)):
            #     if correctLetters[i].isalpha():
            #         if correctLetters[i].isupper():
            #             if ans[i] != correctLetters[i].lower():
            #                 removeFromAnswers = True
            #                 # pass
            #         elif correctLetters[i].islower():
            #             if correctLetters[i].lower() not in ans:
            #                 removeFromAnswers = True
                            # pass
        if removeFromAnswers != len(correctLetters):
            list(Answers_Left).remove(ans)
        else:
            ans = "".join(ans)
            if wordScores[ans][0] > maxScore:
                bestGuess = ans
                maxScore =  wordScores[ans][0]
    print(bestGuess)
    return bestGuess



def attempt(Sequence, Guess):

    load_all_possible_answers()
    PastGuessInfo = loadPastGuessInfo()
    if PastGuessInfo == []:
        GuessNum = 1
    else:
        GuessNum = len(PastGuessInfo)
    wrongLetters = GetPastIncorrectLetters(PastGuessInfo, Sequence, Guess)
    PastCorrectLetters = GetPastCorrectLetters(PastGuessInfo, Sequence, Guess)
    SavePastGuesses(Sequence, Guess, GuessNum, PastCorrectLetters, wrongLetters)
    WordScores = scoreWords(scoreLetters(), GuessNum)
    Possible_Answers_Left = Possible_Words_Left(Sequence, Guess, wrongLetters, GuessNum, WordScores)
    return PickBestWord(Possible_Answers_Left, PastCorrectLetters, Sequence, Guess, WordScores)

if __name__ == '__main__':
    attempt(sys.argv[1], sys.argv[2])
