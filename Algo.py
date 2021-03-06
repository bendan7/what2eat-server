import csv
import json
import os
import sys
import threading
import glob
from time import sleep


class Algo():

    def __init__(self):
        # print("init algo object")
        self.recNum=1000
        datasize = str(self.recNum)+"data/"  # fulldata || 1000data
        # TODO: write code for the case the file doesnt found

        self.__location__ = os.path.realpath(
            os.path.join(os.getcwd(), os.path.dirname(__file__)))

        self.data_file = open(os.path.join(self.__location__, datasize+'data.csv'), newline='')
        self.attr_file = open(os.path.join(self.__location__, datasize+'attNames.csv'))
        self.dishes_file = open(os.path.join(self.__location__, datasize+'DishesIds.csv'))
        self.preview_file = open(os.path.join(self.__location__, 'recPreview.json'), encoding='utf-8')

        self.attArr = self.attr_file.readline().split(',')
        self.dishesArr = self.dishes_file.readline().split(',')

        self.DISHES_THRESHOLD = 10
        self.NUMBER_OF_ATTR = len(self.attArr)
        self.NUMBER_OF_DISHES = len(self.dishesArr)
        self.lock = threading.Lock()

        # init empty gini-rates list with none
        self.giniRates = [None] * self.NUMBER_OF_ATTR

        # init Relevant Rows arr
        self.RR = [1] * self.NUMBER_OF_ATTR

        # init Relevant columns arr
        self.RC = [1] * self.NUMBER_OF_DISHES
        self.NumberOfRelevantAtt = self.NUMBER_OF_ATTR

        self.data_reader = csv.reader(self.data_file, delimiter=',', quotechar='|')

        self.indexAttWithMaxGini=-1

        self.lock.acquire()
        self.calcTheNextAtt() # this function update the 'nextAtt' var
        self.lock.release()

    def print1_5(self):
        for i in range(1,1000):
            self.lock.acquire()
            print(threading.get_ident())
            self.lock.release()

    def print6_10(self):
        for i in range(1,6):
            # self.lock.acquire()
            print(threading.get_ident())
            # self.lock.release()

    def calcGini(self,no, yes):
        return 1 - (yes / self.NUMBER_OF_DISHES) ** 2 - (no / self.NUMBER_OF_DISHES) ** 2

    def readSpecificLine(self, lineNumber, file):
        file.seek(0)
        for i, line in enumerate(file):
            if i == lineNumber:
                return line
        return "ERROR: LINE #" + str(lineNumber) + " DOESN'T FOUND"

    #  NumOfRelevantDishes < DISHES_THRESHOLD
    def areWeDone(self):
        return True if sum(self.RC) <= self.DISHES_THRESHOLD else False

    # AND operator that work with 2 arrays
    def AND(self,A, B):
        leng = len(A)
        for i in range(0, leng):
            if A[i] == 1 & B[i] == 1:
                A[i] = 1
            else:
                A[i] = 0
        return A

    def getNumOfRelevantDishes(self):
        return self.NUMBER_OF_DISHES

    # this method calc the next att that need to be ask and update the var 'nextAtt'
    # return 1 if the threshold reach, else 0
    def calcTheNextAtt(self):
        if self.areWeDone() == False:
            # return for the file start
            self.data_file.seek(0)

            i = 0
            for row in self.data_reader:
                # If the Row in relevant
                if self.RR[i]:
                    yesCount = 0
                    noCount = 0
                    j = 0
                    for cell in row:
                        if self.RC[j]:
                            if cell == '0':
                                noCount += 1
                            else:
                                yesCount += 1
                        j += 1
                    self.giniRates[i] = self.calcGini(noCount, yesCount)
                # the else section can be remove for optimize the performers
                else:
                    self.giniRates[i] = -1
                # print section : for dev
                # print(str(row) + str(RR[i]) + "  " + AttArr[i] + "  zero:" + str(noCount) + "  one:" + str(yesCount) +
                #       "  Gini Rate:  " + str(giniRates[i]))
                i += 1

            # TODO: random attr choices effected by this line
            # return first instance of the largest valued
            self.indexAttWithMaxGini = self.giniRates.index(max(self.giniRates))
            self.attWithMaxGini = self.attArr[self.indexAttWithMaxGini]

            return 0
        else:
            return 1  # the num of dishes reach to the threshold

    # this method get the respond for the "ask att" and update the RC & RR array.
    # in addition make a call to 'calcTheNextAtt' method
    # return 1 if the threshold reach, else 0
    def respon(self,answer):

        self.NumberOfRelevantAtt = self.NumberOfRelevantAtt - 1

        # the client can't ask the next att before this
        # section finish to compute the respond to the last att
        self.lock.acquire()

        # "i don't have" case
        if answer == "0":
            print("algo update:NOT " + self.attWithMaxGini)
            # update the relevant dishes arr
            # this pip line: read-line-> split -> to int -> inverse 0>1 & 1>0
            # (the inverse because its "i don't have" case)
            reverseRow = list(map((lambda x: 1 if x == 0 else 0),
                                  [int(x) for x in self.readSpecificLine(self.indexAttWithMaxGini, self.data_file).split(',')]))
            self.RC = self.AND(self.RC, reverseRow)

        # "i have" case
        if answer == "1":
            print("algo update:YES " + self.attWithMaxGini)
            attRow = list(map(int, self.readSpecificLine(self.indexAttWithMaxGini, self.data_file).split(',')))
            self.RC = self.AND(self.RC, attRow)

        # the section run after we update the arrays with the answer that we get from the client
        self.NUMBER_OF_DISHES = sum(self.RC)
        areWeDone = self.calcTheNextAtt()
        self.lock.release()
        return areWeDone

    def getNextAtt(self):
        return self.attWithMaxGini

    def getAttImage(self):
        urlsFile='smallImagesUrl.json'
        with open(os.path.join(self.__location__,urlsFile),'r') as imagesFile:
            urls=json.load(imagesFile)
            return(urls[self.attWithMaxGini])

    def getRecipesId(self):
        recIds=[]
        for i in range(self.recNum):
            if(self.RC[i]):
                recIds.append(self.dishesArr[i])
        return recIds

    def getPreviewInfo(self):
        #if we are not finish return an empty list
        if not self.areWeDone():
            return []
        allRecipeURL='https://www.allrecipes.com/recipe/'
        recIds=self.getRecipesId()
        relJson=[]
        for rec in self.preview_file:
            recipe=json.loads(rec)
            rid = str(recipe['id'])
            recipe['recipeURL']=allRecipeURL+rid
            for id in recIds:
                if rid==id:
                    relJson.append(recipe)
        return relJson