import pandas as pd
from bs4 import BeautifulSoup as bs
import requests
from keyCombo.keyComboFinder import combify
from keyCombo.comboData import stopwords
import re
import time
#############################
import inflection
#from nltk.corpus import wordnet
import nltk
import nltk.data
from nltk.tokenize import PunktSentenceTokenizer
nltk.download('punkt')
#############################
from spinrewriter import SpinRewriter
rewriter = SpinRewriter('info@sussexseo.net', '82109b0#51de401_45b0364?5ada2fd')



URLfilename = "Full3.csv"
MatchingFileName = "Plumbing Entities2.csv"

API = 0



def scrape_and_grab(link):
  user = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
  agent = "(KHTML, like Gecko) Chrome/74.0.3729.108 Safari / 537.36"
  user_agent = user + agent

  try:
    resp = requests.get(link, headers={'User-Agent': user_agent}, timeout=20, verify=True)
    headers = ["h1", "h2", "h3"]
    soup = bs(resp.text, 'lxml')


    page = []
    #relatedTerms = []
    for header in soup.find_all(headers):
        headerText = header.get_text().strip()
        #check for matching words in heading
        found_words = [word for word in Matching if word in headerText]
        if (found_words):
            little_dict = {"HEADING": headerText}
        else: 
            #Do nothing for that heading where no matching word found
            continue
        
       
        for elem in header.next_siblings:
            if elem.name and elem.name.startswith('h'): # case if next element is header too
            
                break  #becaus we are dropping that header 
            if elem.name == 'p': #case if next element is paragraph
                paragraphText = elem.get_text().strip()
                #check for matching words in paragraph
                found_words = [word for word in Matching if word in paragraphText]
                if (found_words):
                    little_dict["PARAGRAPH"] = paragraphText
                    page.append(little_dict)
                    #relatedTerms = found_words
                    #     
    print("OK : " + link)
    if (page and relatedTerms):
        return(page)
    
    
  except requests.exceptions.RequestException:
    print ("ERROR : " + link)
    #print (e)

def findTopic(word,Heading,paragraph):
    if word in Heading:
        return(word,Heading,paragraph)

def findSentences(word,sentence):
    if word in sentence:
        return word,sentence
        
def findWholeWord(w):
    return re.compile(r'\b({0})\b'.format(w), flags=re.IGNORECASE).search


def createTopic(DF,Term,combos):
    # print("DF :",DF)
    # print("Term :",Term)
    #print("combos :",combos)
    dfObj = pd.DataFrame(columns=['Related Term','Heading','Paragraph','Topic'])
    for index, row in DF.iterrows():
        for word in combos:
            result = findWholeWord(word)(row['Heading'])
            #result = findTopic(word.lower(),row['Heading'].lower(),row['Paragraph'])
            wordGroup = inflection.singularize(word)+","+inflection.pluralize(word)
            if result is not None:
                #print("Found : ",wordGroup," in ",row['Heading'])
                #word,Heading,paragraph = result
                dfObj = dfObj.append({'Related Term':Term,'Heading': row['Heading'],'Paragraph': row['Paragraph'],'Topic':wordGroup}, ignore_index=True)

    dfObj = dfObj.groupby('Heading').agg({'Related Term':'first','Paragraph':'first','Topic': ', '.join}).reset_index()  #Group by Heading   
    dfObj = dfObj[['Related Term','Heading','Paragraph','Topic']] #Re-arranging again
    ##Fix for single heading#####
    dfObj['Count'] = dfObj.groupby('Topic')['Topic'].transform('count')
    dfObj = dfObj[dfObj["Count"] >= 2]
    ######
    dfObj = dfObj.sort_values(by="Topic", ascending=False)
    #print (dfObj)
    return (dfObj)


def generateSpintax(DF,combos):
    #returns spintext
    df = DF.groupby('Word').agg({'Sentence': ' |'.join}).reset_index()
    df['Sentence'] = ('{' + df['Sentence'] + '}')
    texd = []
    for index, row in df.iterrows():
        texd.append(row["Sentence"])
    spintaxInput = ' '.join(texd)
    combos = list (combos)
    global API
    API = API + 1
    print ("API CALL : ", API)
    time.sleep(7)
    #print(spintaxInput)
    spintaxInput = " ".join(spintaxInput.split())
    #print(spintaxInput)
    response = rewriter.api._transform_plain_text('text_with_spintax', spintaxInput, combos, 'high')
    return(response["response"])
    #return (spintaxInput.rstrip())

def groupFix(DF,Topic):
    #Get data for each group
    texd = []
    headings = []
    for para,heading in zip(DF["Paragraph"],DF["Heading"]):
    
        texd.append(para) 
        text = ' '.join(texd)

        headings.append(heading) 
        headingText = ' | '.join(headings)
     
    return (text,headingText)    

def combifyTopic(DF):
    #print (DF)
    term = str(DF['Related Term'].iloc[0])
    grouped_topic = DF.groupby('Topic')
    
    fd = pd.DataFrame(columns=['Term','Heading','Spintext'])
    for key, item in grouped_topic:
        dfObj = pd.DataFrame(columns=['Sentence','Word','Heading']) # new everytime
        #print("Topic : ",key)
        Topic = key
        text,headingText = groupFix(grouped_topic.get_group(key),key)
   
        #Calculate Combos for paragraphs
        combos = combify(text, 1, stop_words=stopwords) # returns datafram
        average = combos["NUMBER_OF_TIMES_FOUND"].mean() # calculate average
        average = average + 1 # Add 1 to average
        df = combos[combos["NUMBER_OF_TIMES_FOUND"] > average] # Filter value based on criteria
        df= df.sort_values(by="NUMBER_OF_TIMES_FOUND", ascending=False) #Sort in Desc
        combos = tuple(list(df.index)) # dataframe to list
        
        #print("Combos : ",combos)
        sent_detector = nltk.data.load('tokenizers/punkt/english.pickle') # Get sentences from paragraphs
        sentences = sent_detector.tokenize(text.strip())
        #print("Sentences : ",sentences)
        
        for sent in sentences:
            for word in combos:
                result = findWholeWord(word)(sent)
                #print(findWholeWord(word)(sent))
                #result = findSentences(word.lower(),sent.lower())
                if result is not None:
                    #word,sentence = result
                    dfObj = dfObj.append({'Word':word,'Sentence': sent,'Heading':headingText}, ignore_index=True)
        #print(dfObj)
        if not dfObj.empty:
            dfObj = dfObj.groupby('Sentence').agg({'Word': ', '.join,'Heading':'first'}).reset_index()  #Group by Heading 
            dfObj = dfObj[['Sentence','Word','Heading']] #Re-arranging again
            dt = dfObj.sort_values(by="Word", ascending=False)
            #dt['Word'] = dt['Word'].str.split(',').sort_values()
            dt['Count'] = dt.groupby('Word')['Word'].transform('count')
            dt['Len'] = dt['Sentence'].str.len() # count chracters
            dt= dt.sort_values(by="Count", ascending=False) #Sort in Desc
            dt = dt[dt["Count"] >= 2]
            # path='Output\\'
            # name = path+key+ '('+term+')'
            # filename = "%s.csv" % name
            # dt.to_csv(filename,index=False, encoding='utf-8-sig')
            ####Spintax###
            if not dt.empty:
                response = generateSpintax(dt,combos)
                headingTextforThis = str(dt['Heading'].iloc[0]) 
                headingTextforThis =  ('{' + headingTextforThis + '}')
                fd = fd.append({'Term':term,'Heading':headingTextforThis, 'Spintext':response}, ignore_index=True)
            
    # filename = "%s.csv" % name
    # fd.to_csv(filename,index=False, encoding='utf-8-sig')
    #print(fd) #retruns 1 terms alll topic spintax
    return (fd)
      
        




def combifyData(DF): 
    grouped_df = DF.groupby('Related Terms')
    dataframes = pd.DataFrame(columns=['Term','Heading','Spintext'])  
    #print(DF)
    for key, item in grouped_df:
        relatedTerm = key
        texd = []
        #print(relatedTerm, "\n\n")
        for heading in item["Heading"]:
            texd.append(heading) 
        text = ' '.join(texd)
        #print(text)
        combos = combify(text, 1, stop_words=stopwords)
        average = combos["NUMBER_OF_TIMES_FOUND"].mean() # calculate average
        average = average + 1 # Add 1 to average
        df = combos[combos["NUMBER_OF_TIMES_FOUND"] > average] # Filter value based on criteria
        df= df.sort_values(by="NUMBER_OF_TIMES_FOUND", ascending=False) #Sort in Desc

        orderedCombos = tuple(list(df.index))
        dfObj = createTopic(grouped_df.get_group(key),relatedTerm,orderedCombos) # function call for each (DF for that related term , related term , and particular combo)

        spintaxDF = combifyTopic(dfObj)
        #print (dfObj)
        frames = [dataframes,spintaxDF]
        dataframes = pd.concat(frames)
        # path='Output\\'
        # dfObj.to_csv(path+relatedTerm+'.csv',index=False, encoding='utf-8')
    dataframes.to_csv("Spintax.csv",index=False, encoding='utf-8')
    print(dataframes)
   
        
      
 

#Read CSV for URLs
df = pd.read_csv(URLfilename,index_col=False) 
#store relavant data
df=df[['URL','Related Terms']]
#Read fil for matching words 
matchFrame = pd.read_csv(MatchingFileName,index_col=False)
#get matching words in list
matchFrame = matchFrame[['matched_text']]
Matching = matchFrame['matched_text'].tolist()
#Dataframe to store URL and Parsed Pages
dfObj = pd.DataFrame(columns=['URL','Related Terms', 'Page'])    
for index, row in df.iterrows():
    #print (row['URL'], row['Related Terms'])
    link = row['URL']
    relatedTerms = row['Related Terms']
    page = scrape_and_grab(link)
    if page is not None: #CHECK for none (IMP) and Store only those with valid data
        if(len(page)!=0):
            dfObj = dfObj.append({'URL': link,'Related Terms':relatedTerms, 'Page': page}, ignore_index=True)


#Create Master Dataframe
History = pd.DataFrame(columns=['URL','Related Terms','Heading','Paragraph']) 
for index, row in dfObj.iterrows(): # for each row (page)
    term = row["Related Terms"]
    url = row["URL"]
    for page in row["Page"]:
        heading = page.get('HEADING')
        paragraph = page.get('PARAGRAPH')
        History = History.append({'URL': url,'Related Terms':term, 'Heading': heading,'Paragraph':paragraph}, ignore_index=True) 

History.drop_duplicates(inplace=True)

combifyData(History)




