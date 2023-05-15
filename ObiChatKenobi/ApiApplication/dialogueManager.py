import random


class Question:
    def __init__(self, phrases, answerVerbs, correctAnswers, describedAnswers):
        self.phrase = ""
        self.phrases = phrases
        self.answerVerbs = answerVerbs
        self.correctAnswers = correctAnswers
        self.describedAnswers = describedAnswers


class Phrase:
    def __init__(self, phrase, sentiment):
        self.phrase = phrase
        self.sentiment = sentiment

class Frame:
    def __init__(self,remainingQuestions,correctAnswers,incorrectAnswers,lastAction):
        self.remainingQuestions=remainingQuestions
        self.correctAnswers=correctAnswers
        self.incorrectAnswers=incorrectAnswers
        self.lastAction=lastAction
    def match(self,otherFrame):
        ret=True
        if(self.remainingQuestions!=-1 and self.remainingQuestions > otherFrame.remainingQuestions):
            ret=False
        if (self.correctAnswers != -1 and self.correctAnswers > otherFrame.correctAnswers):
            ret = False
        if (self.incorrectAnswers != -1 and self.incorrectAnswers > otherFrame.incorrectAnswers):
            ret = False
        if (self.lastAction != "*" and self.lastAction != otherFrame.lastAction):
            ret = False
        return ret

FAILED_TEST = Frame(-1,-1,2,"*")
PASSED_TEST = Frame(-1,2,-1,"*")
START_TEST = Frame(-1,-1,-1,"START")
WRONG_ANSWER_FRAME = Frame(-1,-1,-1,"FALSE")
CORRECT_ANSWER_FRAME = Frame(-1,-1,-1,"TRUE")
UNKNOWN_ANSWER_FRAME = Frame(-1,-1,-1,"UNK")


class DialogueManager:
    def __init__(self):
        self.questionsToAsk = []
        self.currentSentiment = 1
        self.welcomAntePhrases = []
        self.correctAntePhrases = []
        self.incorrectAntePhrases = []
        self.failedTestPhrases=[]
        self.passedTestPhrases=[]
        self.unknownAntePhrases = []
        self.askedQuestion = None
        self.chosenWelcomAntePhrase = None
        self.chosenCorrectAntePhrases = None
        self.chosenIncorrectAntePhrases = None
        self.chosenUnknownAntePhrases = None
        self.correctAnswers=0
        self.wrongAnswers=0
        self.dialogueAction = [("START", "START")]
        self.questionsToAsk.append(Question(["how old is a 7 years old?"], ["be"], ["7", "7 years", "7 years old"],
                                            ["7 years old was the right answer, let's move on, "]))
        self.questionsToAsk.append(Question(["in which country does Rome reside"], ["be", "reside"], ["italy"],
                                            ["it resides in Italy, but now let's go to the next question: ",
                                             "last time i check it was in Italy! But i may be wrong, let's keep going: "]))
        self.questionsToAsk.append(Question(["can a priest get married?"], ["be", "can"], ["no", "not"],
                                            ["he absolutely can't, let's go on and try with another question: "]))

        self.welcomAntePhrases.append(Phrase(
            "Welcome young student! Thrilled to become a jedi? This if your first question to check if you are good: ",
            1))
        self.welcomAntePhrases.append(Phrase(
            "Hello there! Are you ready to become a jedi? Let's see if you have studied enough: ", 1))

        self.failedTestPhrases.append(Phrase(
            "Young student, you clearly aren't prepared, don't let the dark side consume you and try again next time.",
            0))
        self.failedTestPhrases.append(Phrase(
            "Sorry young student, but you haven't studied enough for this test! Try again in a while and you will succsed.", 1))
        self.failedTestPhrases.append(Phrase(
            "I'm really sorry, student but you haven't passed the exam, if you need help to study you can ask me any time.",
            2))

        self.passedTestPhrases.append(Phrase(
            "Well you clearly studied, you can become a padawan but be careful about the dark side, i feel disturbance in you soul.",
            0))
        self.passedTestPhrases.append(Phrase(
            "Congratulations you have studied, you have passed the test and can officialy become a padawan! good luck on becoming a Jedi.",
            1))
        self.passedTestPhrases.append(Phrase(
            "I'm amazed from your performance, you clearly have what it needs to become a good padawan and hopefully a good Jedi.",
            2))

        self.correctAntePhrases.append(Phrase("Correct but this question was simple. let's keep going, next question: ", 0))
        self.correctAntePhrases.append(Phrase("It's correct. let's keep going, next question: ", 1))
        self.correctAntePhrases.append(Phrase("Good answer! let's keep going, next question: ", 2))

        self.incorrectAntePhrases.append(Phrase("That's not right! you must study more!! ", 0))
        self.incorrectAntePhrases.append(Phrase("That's not right! ", 1))
        self.incorrectAntePhrases.append(Phrase("That's not right! but don't lose your belief, ", 2))

        self.unknownAntePhrases.append(
            Phrase("Sorry youngling but i can't understand you, could you answer me again: ", 0))
        self.unknownAntePhrases.append(
            Phrase("Sorry youngling but i can't understand you, could you answer me again: ", 1))
        self.unknownAntePhrases.append(
            Phrase("Sorry youngling but i can't understand you, could you answer me again: ", 2))

    def getQuestion(self):
        converstaionStatus=Frame(len(self.questionsToAsk),self.correctAnswers,self.wrongAnswers,self.dialogueAction[len(self.dialogueAction) - 1][1])
        if FAILED_TEST.match(converstaionStatus):
            self.askedQuestion = Question([], [], [], [])
            self.askedQuestion.phrase = random.choice(
                [p.phrase for p in self.failedTestPhrases if p.sentiment == self.currentSentiment])
        elif PASSED_TEST.match(converstaionStatus):
            self.askedQuestion = Question([], [], [], [])
            self.askedQuestion.phrase = random.choice(
                [p.phrase for p in self.passedTestPhrases if p.sentiment == self.currentSentiment])
        elif START_TEST.match(converstaionStatus):  # It means we are starting the conversation
            self.askedQuestion = random.choice(self.questionsToAsk)
            self.questionsToAsk.remove(self.askedQuestion)
            self.chosenWelcomAntePhrase = random.choice([p.phrase for p in self.welcomAntePhrases if p.sentiment == self.currentSentiment]) #filtered by sentiment
            self.askedQuestion.phrase = self.chosenWelcomAntePhrase + random.choice(
                self.askedQuestion.phrases)
        elif CORRECT_ANSWER_FRAME.match(converstaionStatus):
            self.askedQuestion = random.choice(self.questionsToAsk)
            self.questionsToAsk.remove(self.askedQuestion)
            self.chosenCorrectAntePhrases = random.choice(
                [p.phrase for p in self.correctAntePhrases if p.sentiment == self.currentSentiment])  # filtered by sentiment
            self.askedQuestion.phrase = self.chosenCorrectAntePhrases + random.choice(
                self.askedQuestion.phrases)
        elif WRONG_ANSWER_FRAME.match(converstaionStatus):
            wrongQuest = self.askedQuestion
            self.askedQuestion = random.choice(self.questionsToAsk)
            self.questionsToAsk.remove(self.askedQuestion)
            self.chosenIncorrectAntePhrases = random.choice(
                [p.phrase for p in self.incorrectAntePhrases if p.sentiment == self.currentSentiment])  # filtered by sentiment
            self.askedQuestion.phrase = self.chosenIncorrectAntePhrases + random.choice(
                wrongQuest.describedAnswers) + random.choice(
                self.askedQuestion.phrases)

        elif UNKNOWN_ANSWER_FRAME.match(converstaionStatus):
            self.chosenUnknownAntePhrases = random.choice(
                [p.phrase for p in self.unknownAntePhrases if p.sentiment == self.currentSentiment])  # filtered by sentiment
            self.askedQuestion.phrase = self.chosenUnknownAntePhrases + random.choice(
                self.askedQuestion.phrases)

        return self.askedQuestion

    def answerQuestion(self, answers):
        if(answers==None):
            return
        self.currentSentiment = answers.sentiment
        trueAnswer = "FALSE"
        if (
                None in answers.complements or None in answers.verbs or None in answers.modifiers):  # If our parsing trew an exception it means we didn't understand the answer
            trueAnswer = "UNK"
        else:  # We understood the answer so we check if it is correct
            for phrase in answers.complements:
                for elem in phrase:
                    if (elem.lower() in self.askedQuestion.correctAnswers):
                        trueAnswer = "TRUE"
        if(trueAnswer=="TRUE"):
            self.correctAnswers+=1
        if(trueAnswer=="FALSE"):
            self.wrongAnswers += 1
        self.dialogueAction.append((self.askedQuestion, trueAnswer))