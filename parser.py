import pandas as pd
from bs4 import BeautifulSoup as bs
import requests
from keyCombo.keyComboFinder import combify
from keyCombo.comboData import stopwords
import json
import inflection

#from nltk.corpus import wordnet


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
    #print("Word  :"+ word +" Heading "+ Heading)
    if word in Heading:
        #print("Found :"+ word +" in "+ Heading)
       
        return(word,Heading,paragraph)


def createTopic(DF,Term,combos):
    # print("DF :",DF)
    # print("Term :",Term)
    print("combos :",combos)
    dfObj = pd.DataFrame(columns=['Related Term','Heading','Paragraph','Topic'])
    for index, row in DF.iterrows():
        for word in combos:
            result = findTopic(word.lower(),row['Heading'].lower(),row['Paragraph'])
            wordGroup = inflection.singularize(word)+","+inflection.pluralize(word)
            if result is not None:
                word,Heading,paragraph = result
                dfObj = dfObj.append({'Related Term':Term,'Heading': Heading,'Paragraph': paragraph,'Topic':wordGroup}, ignore_index=True)

    dfObj = dfObj.groupby('Heading').agg({'Related Term':'first','Paragraph':'first','Topic': ', '.join}).reset_index()  #Group by Heading   
    dfObj = dfObj[['Related Term','Heading','Paragraph','Topic']] #Re-arranging again
    #print (dfObj.sort_values(by="Topic", ascending=False))
    return (dfObj.sort_values(by="Topic", ascending=False))

          


def combifyData(DF): 
    grouped_df = DF.groupby('Related Terms')
    dataframes = pd.DataFrame(columns=['Related Term','Heading','Paragraph','Topic'])  
    #print(DF)
    for key, item in grouped_df:
        relatedTerm = key
        texd = []
        #print(relatedTerm, "\n\n")
        for heading in item["Heading"]:
            #print([d['PARAGRAPH'] for d in pages])
            texd.append(heading)
        #textPerTerm = [i for sublist in texd for i in sublist]
        
        text = ' '.join(texd)
        #print(text)
        combos = combify(text, 1, stop_words=stopwords)
        average = combos["NUMBER_OF_TIMES_FOUND"].mean() # calculate average
        average = average + 1 # Add 1 to average
        df = combos[combos["NUMBER_OF_TIMES_FOUND"] > average] # Filter value based on criteria
        df= df.sort_values(by="NUMBER_OF_TIMES_FOUND", ascending=False) #Sort in Desc

        orderedCombos = tuple(list(df.index))
        dfObj = createTopic(grouped_df.get_group(key),relatedTerm,orderedCombos) # function call for each (DF for that related term , related term , and particular combo)
        #print (dfObj)
        frames = [dataframes,dfObj]
        dataframes = pd.concat(frames)
    # path='Output\\'
    # dfObj.to_csv(path+relatedTerm+'.csv',index=False, encoding='utf-8')
    dataframes.to_csv("Output.csv",index=False, encoding='utf-8')
    #print(dataframes)
   
        
      
 

#Read CSV for URLs
df = pd.read_csv("Full2.csv",index_col=False) 
#store relavant data
df=df[['URL','Related Terms']]

matchFrame = pd.read_csv("Plumbing Entities2.csv",index_col=False)
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

##################################################### HISTORY ##################################################################

History = pd.DataFrame(columns=['URL','Related Terms','Heading','Paragraph']) 
for index, row in dfObj.iterrows(): # for each row (page)
    term = row["Related Terms"]
    url = row["URL"]
    for page in row["Page"]:
        heading = page.get('HEADING')
        paragraph = page.get('PARAGRAPH')
        History = History.append({'URL': url,'Related Terms':term, 'Heading': heading,'Paragraph':paragraph}, ignore_index=True) 

History.drop_duplicates(inplace=True)
#print(History)
##########################################################################################################################

combifyData(History)




