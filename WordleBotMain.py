from os import remove
import sys


Possible_Answers = []
Possible_Answers_Left = []
bestGuesses = []
global correctLetters
debug = False


# Future improvements possible:
### Store past guesses and their sequence in a csv or JSON file so that it can be read in (this way you don't have to pass it as an arg)

### better way to score letters/words
###         - Maybe also a longer list of test words
###         - This could just be used to more accurately score letters/words, including words longer than 5 letters

### A way to decide when to introduce words with "letter multiples" (words with the same letter more than once)
###         - Currently I don't introduce letter multiples until at least the third guess, but it's possible before that, in which case the bot returns null


### Improve how we consider past "Green" or "Yellow" letters! Currently the only consideration is if the letter is IN the word, not what it's location in the word is


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
    return Possible_Answers_Left, correctLetters



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


def attempt(Sequence, Guess, GuessNum, PastCorrectLetters, wrongLetters = ""):


    load_all_possible_answers()
    # letScores = scoreLetters()
    # sort_lettersScores = sorted(letScores.items(), key=lambda x: x[1])

    WordScores = scoreWords(scoreLetters(), GuessNum)
    sort_WordScores = sorted(WordScores.items(), key=lambda x: x[1])

    Possible_Answers_Left, correctLetters = Possible_Words_Left(Sequence, Guess, wrongLetters, GuessNum, WordScores)
    return PickBestWord(Possible_Answers_Left, PastCorrectLetters, Sequence, Guess, WordScores)




if __name__ == '__main__':
    attempt(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
