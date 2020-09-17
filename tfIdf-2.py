#Marc Paul

import re
from nltk.corpus import stopwords  
import math
import csv

class ifidf:
    #here we are getting the data from our csv files and putting them in a dictionary. We have a fair amount of code because
    #put them into the library without creating groups of two 
    def importInvertedDic(self, file, maxDocNum):
        invertedIndex = dict()
        with open(file) as f:
            reader = csv.DictReader(f, 'r')
            for a in reader:
                for b in reader:
                    g = list(b.values())
                    temp = g[1][1]
                    hater = []
                    tempNums = re.findall(r'\d+(?:,\d+)?', temp)
                    intTemp = [int(i) for i in tempNums]
                    prev = 0
                    counter = 0
                    for hate in intTemp:
                        counter = counter + 1
                        if(counter == 2):
                            temp = [prev, hate]
                            hater.append(temp)
                            counter = 0
                            if(prev > maxDocNum):
                                maxDocNum = prev
                            prev = hate
                        else:
                            prev = hate
                    invertedIndex[g[0]] = {'Frequency': int(g[1][0]), 'Occurrences': hater}
        return invertedIndex
    
                
    #this is our queue cleaner. We use this to make our queue have similar qualities to our inverted index.
    #we use a re to clean the queue and return it back . We also check to make sure it's not empty.
    def queryCleaner(self, query):
        queryList = query.split()
        importantQueries = []
        for i in range(len(queryList)):
            content = queryList[i]
            content = content.lower()
            content = re.sub(r"\d+", "", content) 
            content = re.sub(r"[*,@\'?\.$%_\\/]", "", content, flags=re.I) 
            content = content.strip()
            if(content != str('')):
                importantQueries.append(content)
        return importantQueries
    
    
    
    #Here we're finding the highest frequency document in every document. 
    #we loop through every document and find a number of occurrence
    #we do another loop and see if that number is higher then our current one
    #if it's not the new maxDoc is our current and we forget the old one.
    def findHighestFreqWordInDoc(self, invertedIndex):
        library = invertedIndex
        docMaxWord= {'DocNum': 'Document Number'}
        for word in library.values():
            for i in range(len(word['Occurrences'])):
                docNum = word['Occurrences'][i][0]
                docFreq = word['Occurrences'][i][1]
                if docNum not in docMaxWord.keys():
                    docMaxWord[docNum] = docFreq
                if(docNum in docMaxWord.keys() and docMaxWord[docNum] < docFreq):
                    docMaxWord[docNum] = docFreq
        return docMaxWord
    
    
    #We're calculating our TF. We do this by taking the amount of times a word is in a document, 
    #and diving it by the highest frequency word in the document. If one of the queue words isn't
    #in our dictionary, we give it a rating of 1/1500
    def calculateTf(self, highestFreqDic, index, query):
        tfDic = dict()
        for key, word in index.items():
            for i in range(len(word['Occurrences'])):
                doc = word['Occurrences'][i][0]
                num = float(word['Occurrences'][i][1])
                maxfreq = float(highestFreqDic[doc])
                tff = float(num/maxfreq)    
                if(key not in tfDic.keys()):
                    tfDic[key] = [[doc, tff]]
                else:
                    tfDic[key].append([doc, tff])
        for word in query:
            if(word not in tfDic):
                tfDic[word] = [[-1, float(1/1500)]]
        return tfDic
                
     #To calculate our IDF we looked at every word in our query, got their frequency
     #if the word wasn't in our dictionary, we gave it a frequency of 1. We divide the amount of times there was a document with the word on it by our total amount of documents
     #The next thing we did was take the log base 2 of our freqInDocs/MaxDocs. We put our idf into a dictionary and returned the dictionary
    def calculateIDF(self, query, index):
        idfDic = dict()
        docCounter = 1500
        decDocCount = float(docCounter)
        for word in query:
            if(word in index):
                freq = float(index[word]['Frequency'])
            else:
                freq = float(1)
            logFreq = float(decDocCount/freq)
            idf = math.log(logFreq, 2)
            idfDic[str(word)] = idf
        return idfDic
        
    #We're taking our numbers from our idf, since it is significantly smaller, and multiplying it by the corresponding tf number
    #we put it in a dictionary and returned the dictionary
    def tfTimesIdf(self, tfDic, idfDic):
        idfTimestf = dict()
        for key, number in idfDic.items():
            flag = False
            for i in range(len(tfDic[key])):
                tfDoc = tfDic[key][i][0]
                tfNum = tfDic[key][i][1]
                tfTimes = float(number) * tfNum
                if(flag == False):
                    idfTimestf[str(key)] = {'Document': list([tfDoc]), 'tf*idf': list([tfTimes])}
                    flag = True
                else:
                    idfTimestf[str(key)]['Document'].append(tfDoc)
                    idfTimestf[str(key)]['tf*idf'].append(tfTimes)
        return idfTimestf
    
    
    #We got our tf of the words in our query by getting the word that appears most in our document and dividing it by the number each word appears.
    #We then grab our idf for each word in our dictionary and multiply it with our current tf
    def tfIdfQuery(self, query,idfDic):
        freq = dict()
        tfidf = dict()
        maxFreq = 0
        for word in query:
            if(word not in freq):
                freq[str(word)] = float(1)
                if(freq[str(word)] > maxFreq):
                    maxFreq = freq[str(word)]
            else:
                freq[str(word)] += float(1)
                if(freq[str(word)] > maxFreq):
                    maxFreq = float(freq[str(word)])
        for word in query:
            div = float(freq[word]/ maxFreq)
            tfidf[word] = float(div)* float(idfDic[word])
        return tfidf
    
    #We had to find the length of all our documents, because the document length * the query length is our denominator for our cosSim. 
    #We did this by grabbing tf *ifd of each word and squaring it. After this we add the previous squared words and square root them at 
    #the very end
    #we also take the document length of the query
    def lengthOfDoc(self, tfTimesIdf, qtfidf):
        docLength = dict()
        sqrdDocLength = dict()
        i = 1
        counter = 1500
        for word in tfTimesIdf.values():
            for i in range(1, counter):
                if(i in word['Document']):
                    lenDic = word['Document'].index(i)
                    if(i not in docLength.keys()):
                        docLength[i] = float(word['tf*idf'][lenDic]) * float(word['tf*idf'][lenDic])
                        i = i + 1
                    else:
                        docLength[i] = docLength[i] + (float(word['tf*idf'][lenDic] * float(word['tf*idf'][lenDic])))
                        i = i + 1
        docLength['query'] = 0
        for number in qtfidf.values():
            if(number != 0):
                qmultiplied = (float(number) * float(number))
                docLength['query'] = qmultiplied + docLength['query']
                
        for doc, numbers in docLength.items():
            sqrdDocLength[doc] = math.sqrt(numbers)
        sqrdDocLength['query'] = (math.sqrt(docLength['query']))
        return sqrdDocLength
    
    #To find the cosSim we need to get the tf * tfidf of each word in the query and then divide that number by the length of
    #the q and the length of the dictionary document. 
    #if there isn't a number for the tf, we give it a 1/1500 tf ratio.
    #after the numbers are figured out and stored in our dictionary, we sort or dictionary by highest-smallest cosSim
    #we print the results to the user!
    def cosSim(self, dLength, tfidq, tfDic, query):
        simDic = dict()
        finalSimDic = dict()
        for doc, leng in dLength.items():
            top = 0
            bottom = float(leng) * float(dLength['query'])
            tfq = 0
            tfidfq = 0
            for word in query:
                if(word in tfDic[word]):
                    lenInTf = tfDic[word].index(word)
                    tfq = float(tfDic[word][lenInTf])
                else:
                    tfq =  float(1/1500)
                tfidfq = float(tfidq[word])
                tempTop =(float(tfq) * float(tfidfq))
                top = top + tempTop
                finaleq = float(top)/float(bottom)
            simDic[finaleq] = doc
        for sim in sorted (simDic.keys(), reverse = True):
            finalSimDic[simDic[sim]] = sim
        return finalSimDic
        
        
      #This is our gui. The bulk of it is text asking the user how/what they would like to search. It's a lot of code
      #with a little meaning. We are getting information from the user for a more personalized experience.
    def guiBuilder(self, maxDocNum):
        ii = ''
        query = ''
        optionsFlag = False
        queryHappyFlag = False
        exitFlag = False
        while(exitFlag == False):
            print("When you would like to exit the program, pelase type exit.")
            stemming = input("Hello, would you like to compare your query with word stemming off or on? (Off/On) \n")
            stopword = input("Would you like to compare your query with stop words? (Off/On) \n")
            stemming = stemming.lower()
            stopword = stopword.lower()
            while(optionsFlag == False):
                optionselector = input("Currently you have word stemming " + stemming + " and stop words " + stopword + ". Would you like to continue or change these options? (Continue/Change) \n")
                optionselector = optionselector.lower()
                if(optionselector == 'change'):
                    changer = input('Would you like to toggle stop words or word stemming? (stop words/word stem) \n')
                    changer = changer.lower()
                    if(changer == 'stop words'):
                        if(stopword == 'on'):
                            stopword = 'off'
                            print('Stop words have been turned off.')
                        elif(stopword == 'off'):
                            stopword = 'on'
                            print('Stop words have been turned on.')
                        elif(changer == 'exit'):
                            exitFlag = True
                            break
                    elif(changer == 'word stemming' or changer == 'wordstemming' or changer == 'word stem' or changer == 'wordstem'):
                        if(stemming == 'on'):
                            print('Word stemming has been turned off.')
                            stemming = 'off'
                        elif(stemming == 'on'):
                            print('Word stemming has been turned on.')
                            stemming = 'on'
                        elif(changer == 'exit'):
                            exitFlag = True
                            break
                    else:
                        print("Please select a valid option.")
                elif(optionselector == 'continue'):
                    optionsFlag = True
                elif(optionselector == 'exit'):
                    exitFlag = True
                    break
                else:
                    print("Please select a valid option.")
            if(stopword == 'on' and stemming == 'on'):
                ii = self.importInvertedDic('invertedIndexAllOn.csv', maxDocNum)
            elif(stopword == 'off' and stemming == 'off'):
                ii = self.importInvertedDic('invertedIndex.csv', maxDocNum)
            elif(stopword == 'on' and stemming == 'off'):
                ii = self.importInvertedDic('invertedIndexWSOn.csv', maxDocNum)
            elif(stopword == 'off' and stemming == 'on'):
               ii = self.importInvertedDic('invertedIndexStemOn.csv', maxDocNum)
            while(queryHappyFlag == False):
                query = input("Please enter the query you'd like to search \n")
                happySearch = input('Would you like to change your query? (Yes/No) \n')
                happySearch = happySearch.lower()
                if(happySearch == 'no'):
                    queryHappyFlag = True
                elif(happySearch == 'yes'):
                    queryHappyFlag = False
                elif(happySearch == 'exit'):
                        exitFlag = True
                        break
            cleanedQ = self.queryCleaner(query)
            frequencies = self.findHighestFreqWordInDoc(ii)
            tf = self.calculateTf(frequencies, ii, cleanedQ)
            idf = self.calculateIDF(cleanedQ, ii)
            tfStaridf = self.tfTimesIdf(tf, idf)
            tfidfQuery = self.tfIdfQuery(cleanedQ, idf)
            lengthOfDocs = self.lengthOfDoc(tfStaridf, tfidfQuery)
            cosSimAnswer = self.cosSim(lengthOfDocs, tfidfQuery, tf, cleanedQ)
            userWants = input('Would you like to see the tf, idf, tfidf, length of documents, or the cosSim? \n')
            userWants = userWants.lower()
            if(userWants == 'tf'):
                wordSelector = input('Which word would you like to see the tf value for? \n')
                wordSelector = wordSelector.lower()
                if(tf[wordSelector] == None):
                    print("I'm sorry, we don't have the tf of this word.")
                else:
                    if(len(tf[wordSelector]) >= 1):
                        print("Here are the values.")
                        print(tf[wordSelector])
            if(userWants == 'idf'):
                wordPicker = input('Please input a word you would like to see the idf of. \n')
                wordPicker = wordPicker.lower()
                pickedIdf = idf[wordPicker]
                if(pickedIdf == None):
                    print('There is no calculated idf for this value.')
                else:
                    print('The idf value for ' + str(wordPicker) + ' is ' + str(pickedIdf) + '.')
            if(userWants == 'tfidf' or userWants == 'tf idf'):
                userD = input('Please type query to see the tfidf of the view or type the word you would like to see the tfidf for. \n')
                userD = userD.lower()
                print('The tfidf of ' + userD + ' in document is ' + tfStaridf[userD] + '.')
            if(userWants == 'length of documents' or userWants == 'length of docs'):
                print(lengthOfDocs)
            if(userWants == 'cossim'):
                print('The search results show: ')
                print(cosSimAnswer)
            if(userWants == 'exit'):
                exitFlag = True
                break
def main():
    obj = ifidf()
    maxDocNum = 1500
    obj.guiBuilder(maxDocNum)
main()