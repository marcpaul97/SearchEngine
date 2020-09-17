#Marc Paul
import csv
import string 
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from nltk import word_tokenize




def getDocuments(highestDocNum): #an equation to get the amount of documents we want on a list
    docList = []
    for i in range(1, highestDocNum):
        newFileName = "doc" + str(i) + ".txt"
        docList.append(newFileName)
    return docList




def create_library(Documents, stopWordsFlag, stemmingWordsFlag):
    library = dict()                                    #here we're basically getting all our data together
    porter = PorterStemmer()                            #we collect all of our documents and we do a lot of the cleaning of the documents here as well
    stop_words = stopwords.words('english')             #we have our stop words.
    for doc in Documents:     #here we finally move into our documents. 
        with open(doc) as docs:   #you'll see a lot of this code is cleaning the text, and there's nothing to exciting about this function
            skipUrl = docs.readline()
            documents = docs.read()
            words = word_tokenize(documents)
            words = [w.lower() for w in words]
            table = str.maketrans('','', string.punctuation)
            stripped = [w.translate(table) for w in words]
            words = [word for word in stripped if word.isalpha()]
            if(stopWordsFlag == True and stemmingWordsFlag == False):
                words = [w for w in words if not w in stop_words]
            elif(stemmingWordsFlag == True and stopWordsFlag == False): #our flags to test our code and to separate our code as you can see down below we use these flags to save 
                #four different types of inverted indexes
                words = [porter.stem(word) for word in words]
            elif(stemmingWordsFlag == True and stopWordsFlag == True):
                words = [w for w in words if not w in stop_words]
                words = [porter.stem(word) for word in words]
            else:
                words = words
            document_title = skipUrl
            docNum = Documents.index(doc)
            docNum = docNum + 1
            if('[' in words):
                words.remove('[')
            elif(']' in words):
                words.remove(']')
            library[document_title] = {"Document Number": docNum, "Content": words}
    temp = terminator(library)
    return temp



#This is creating our inverted index. It's a fairly simple process. We go by the words that have come from our dictionary
#these are already clean so we can go right into organizing and arranging them.
#if the word isn't already in the inverted index we put it in and we put the corresponding freq, and occurrences
#if it is in the inverted index we make the freq go up by one and put the corresponding occurrence in the correct place
def terminator(dictionary):
    inverted_index = dict()
    for doc in dictionary.values():
        for word in doc['Content']:
            if word not in list(inverted_index.keys()):
                inverted_index[word] = {'Frequency': 1, 'Occurrences': list([[doc['Document Number'], 1]])}
            elif str(word) in list(inverted_index.keys()):
                doc_is_in_occurrence_list = False
                for i in range(len(inverted_index[str(word)]['Occurrences'])):
                    if (inverted_index[str(word)]['Occurrences'][i][0] == doc['Document Number']):
                        inverted_index[str(word)]['Occurrences'][i][1] += 1
                        doc_is_in_occurrence_list = True
                if doc_is_in_occurrence_list == False:
                    inverted_index[str(word)]['Frequency'] += 1
                    inverted_index[str(word)]['Occurrences'].append([doc['Document Number'], 1])   
    return  inverted_index


#we chose to save our files in csv files because we can bring them up in excel if need be and look 
#at them to try and find inconsistencies. These four functions are the exact same thing, except the csv
#file names are different and the flags are different, one for each case required.
def saveToCsvFileAllOff(Docs): #our basic inverted index
    stopWordsFlag = False
    stemmingWordsFlag = False
    invertedIndex = create_library(Docs, stopWordsFlag, stemmingWordsFlag)
    w = csv.writer(open("invertedIndex.csv", "w"))
    for key, value in invertedIndex.items():
        w.writerow([key, value['Frequency'], value['Occurrences']])
        
def saveToCsvFileWSOn(Docs): #made a separate csv for only word stop on
    stopWordsFlag = True
    stemmingWordsFlag = False
    invertedIndex = create_library(Docs, stopWordsFlag, stemmingWordsFlag)
    w = csv.writer(open("invertedIndexWSOn.csv", "w"))
    for key, value in invertedIndex.items():
        w.writerow([key, value['Frequency'], value['Occurrences']])
        
def saveToCsvFileStemOn(Docs): # made a separate csv for only stem words on
    stopWordsFlag = False
    stemmingWordsFlag = True
    invertedIndex = create_library(Docs, stopWordsFlag, stemmingWordsFlag)
    w = csv.writer(open("invertedIndexStemOn.csv", "w"))
    for key, value in invertedIndex.items():
        w.writerow([key, value['Frequency'], value['Occurrences']])

        
def saveToCsvFileAllOn(Docs): #made a separate csv for both stem and stop words 
    stopWordsFlag = True
    stemmingWordsFlag = True
    invertedIndex = create_library(Docs, stopWordsFlag, stemmingWordsFlag)
    w = csv.writer(open("invertedIndexAllOn.csv", "w"))
    for key, value in invertedIndex.items():
        w.writerow([key, value['Frequency'], value['Occurrences']])


highestDocNum = 1500 #could only get to 1500 pages. We believe this is due to our poor internet.
Docs = getDocuments(highestDocNum)   
saveToCsvFileAllOff(Docs)
saveToCsvFileWSOn(Docs)
saveToCsvFileStemOn(Docs)
saveToCsvFileAllOn(Docs)
