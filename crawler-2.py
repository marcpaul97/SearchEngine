#Daniel DeRemigi and Marc Paul

import requests
import time
import re


#created a header to make the web crawler look more realistic.
headers = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36'}

#reads the html and converts it to texts
def htmlReader(file):
    allContent = []
    processedText = []
    finishedText = []
    content = re.compile(r"(<p>)(.*)(</p>)")
    moreContent = content.findall(file)
    
    for i in moreContent:
        allContent.append(i[1])
        
#We do a little cleaning here to make our lives a little easier.
    for word in allContent:
        processedText = cleaner(word)
        finishedText.append(processedText)
    return finishedText
    
def cleaner(words):
    #This is where we really do our cleaning. We split the words, remove all of the
    #punctuation, remove the numbers and make it so only alpha characters are in the sttring
    splitWords = words.split()
    noPeriods = periodCleaner(splitWords)
    noNumbers = numberCleaner(noPeriods)
    realClean = cleanAlphabet(noNumbers)
    return realClean
    

#We remove all the punctuation
def periodCleaner(content):
    for periods in content:
        ind = content.index(periods)
        removePeriod = re.compile(r"\.|\?|!")
        searches = removePeriod.search(periods) 
        if(searches == None):
            content[ind] = re.sub(r"\.|\?|\!", r"", periods)
    return content

#Make it so it's only 0-9 and letters
def cleanAlphabet(content):
    for slang in content:
        ind = content.index(slang)
        content[ind]  = re.sub(r"[^0-9A-Za-z <>\/]+", r"", slang)
    return content

#We get rid of any numbers
def numberCleaner(content):
    for nums in content:
        ind = content.index(nums)
        content[ind] = re.sub(r"\d+", r"", nums)
    return content

        
    #This is where we grab the urls and append them to our stack. We have a terrible variable for our stack (word)
def gettingUrls(words):
    stack = []
    urlList = []
    for urls in words:
        url = re.compile(r'href=[\'|"](.*?)[\'"].*?>')
        findallUrls = url.findall(urls)
        urlList.append(findallUrls)
        

    for i in range(0, len(urlList)):
        if(urlList[i] != []):
                stack.append(urlList[i])
    return stack
#Cleaning the stack to to make it able to be red and put into our big function
def stackCleaning(stack):
    dirty = []
    for i in range(len(stack)):
        dirty.append(stack[i][0])
        
        #this is where we check the raw url/html/css and any other configuration requests can grab, and make sure it
        #is a viable, executable url.
        #if it isn't we throw it away
    cleaned = lotsOfChecks(dirty)
    cleanest = urlPassFail(cleaned)
    mrStrongClean = [x for x in cleanest if x]
    return mrStrongClean

    

#Here we have the very impressive and very kind Mr.Robot
#we keep him away from the bad people who don't want him to see their site
#we start him at the beginning url (muhlenbergs)
def robotWatch(beginingUrl):
    getRobots = requests.get(beginingUrl + "/robots.txt")
    content = getRobots.text
    contentList = content.splitlines()
    badList = []
    
    for bad in contentList:
        disables = re.compile(r"(Disallow: )(.*)")
        searches = disables.search(bad)
        if(searches != None):
            badList.append(searches.group(2))
    return badList
    
    
    
#this is a lot of cleaning and it's fairly effective. We're able to get around 2,0000
#files and then our crawler goes idle, we tried to counter this by giving him a timeout,
#but he seems to need to rest so we've been nice and let him
#we believe this may be to our not so great internet but we're not 100% sure
def lotsOfChecks(dirtyStack):
    cleaned = []
    for checks in dirtyStack:
        checks = re.sub(r"mailto", "", checks)
        checks = re.sub(r"^[:].*", "", checks)
        checks = re.sub(r"^[.].*", "", checks)
        checks = re.sub(r".*[.css]$", "", checks)
        checks = re.sub(r"/media\/.*", "", checks)
        checks = re.sub(r"https\:\/\/fonts\.googleapis", "", checks)
        checks = re.sub(r"https://docs.google.com.*", "", checks)
        checks = re.sub(r"\#.*", "", checks)
        checks = re.sub(r"tel:.*", "", checks)
        checks = re.sub(r"^\/$", "", checks)
        if(checks.startswith("http") or checks.startswith("/")):
            cleaned.append(checks)
    return cleaned
    

        

#seeing if Url is empty or not
def urlPassFail(cleanedStack):
    for url in cleanedStack:
        if(url == '' or url == "" or url == None):
            ind = cleanedStack.index(url)
            del cleanedStack[ind]
    return cleanedStack

#a 10000 time loop to get our web files
def getTenThousandWebPages(stack, beginingUrl, visited, docNum):

    for i in range(1,10000):

        changes = re.compile(r"^[/]")
        matches = changes.match(stack[i])
        #checking the status code to make sure the website says it's aye okay to visit!
        if(matches != 200):
            nextUrl = stack[i]
        if(matches == None):
            nextUrl = stack[i]

        else:
            #if the web link is a relative link we need to make it an absolute link
            nextUrl = beginingUrl + stack[i]


        
        if(nextUrl not in visited):
            #we added a try or two to try and counter any errors we happen to stumble upon
            try:
                #we have our fun requests with a header and a timeout period, giving us a fairly good chance of being successful
                requestNextUrl = requests.get(nextUrl,headers = headers ,timeout = 10)
            except requests.exceptions.ConnectionError:
                requests.status_code = "Connection refused"
                requests.status_code = "raise InvalidSchema"
            content = requestNextUrl.text
            contentList = content.split()
            procsessedContentList = gettingUrls(contentList)
            cleaned = stackCleaning(procsessedContentList)
            #we are back from the url and have downloaded all we need
            for url in cleaned:
                if(url not in stack[i] and url not in visited):
                    stack.append(url)
                    #if we haven't visited the pages url's we add them to our stack and if we have we 
                    #look at making a file
            newFileName = "doc" + str(docNum) + ".txt"
            docNum = docNum + 1
            print("\n" + newFileName + " has been created!. \n")
            f = open(newFileName, "w+")
            f.write(nextUrl)
            f.write(" ")
            f.write("\n")
            htmls = htmlReader(content)
            #we create a file with everything the website had on it and then we close it
            for x in htmls:
                for word in x:
                    f.write(word + " ")
            f.close()
            visited.append(nextUrl)
            #we know we're supposed to be around 1 second, but we've had better results with .5 (Again, we think because of our internet)
            time.sleep(3)
                    
        
        

def main():
    docNum = 1
    
    visited = []
    stack = []
    beginingUrl = "http://www.muhlenberg.edu" #beginning url
    startCrawler = requests.get(beginingUrl, headers = headers , timeout = 5) #our crawler with everything we need in it 
    content = startCrawler.text #starting the magical adventure
    contentList = content.split()
    stack = gettingUrls(contentList)
    cleanedStack = stackCleaning(stack)
    noGoList = robotWatch(beginingUrl) #our personal favorite and apperently our crawlers's too!
    for bad in noGoList:
        visited.append(bad)
    newFile = open("doc0.txt", "w+")
    newFile.write(beginingUrl)
    readableHTML = htmlReader(content)
    
    for i in readableHTML:
        for word in i:
            newFile.write(word + " ")
    newFile.close
    getTenThousandWebPages(cleanedStack, beginingUrl, visited, docNum) #10000 iterations. 
    
main()
    
    
    
    






