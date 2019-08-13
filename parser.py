import pandas as pd
from bs4 import BeautifulSoup as bs
import requests
from keyCombo.keyComboFinder import combify
from keyCombo.comboData import stopwords
import json
import inflection

def scrape_and_grab(link):
  user = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
  agent = "(KHTML, like Gecko) Chrome/74.0.3729.108 Safari / 537.36"
  user_agent = user + agent

  try:
    resp = requests.get(link, headers={'User-Agent': user_agent}, timeout=20, verify=True)
    headers = ["h1", "h2", "h3", "h4", "h5", "h6"]
    soup = bs(resp.text, 'lxml')


    page = []
    #relatedTerms = []
    for header in soup.find_all(headers):
        headerText = header.get_text().strip()
        # print("Header Tag content :")
        # print(headerText)
        little_dict = {"HEADING": headerText}
       
        for elem in header.next_siblings:
            if elem.name and elem.name.startswith('h'): # case if next element is header too
            
                break  
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

def findTopic(word,Heading):
    if word in Heading:
        #print("Found :"+ word +" in "+ Heading)
        #print (inflection.singularize(word))
        return(word,Heading)


def createTopic(DF,Term,combos):
    # print("DF :",DF)
    # print("Term :",Term)
    # print("combos :",combos)
    texd = []
    for index, row in DF.iterrows(): # for each row (page)
        #print(row["Page"])
        #print([d['HEADING'] for d in row["Page"]])
        texd.append([d['HEADING'] for d in row["Page"]])
    HeadingsPerTerm = [i for sublist in texd for i in sublist]
    
    # print("\n\n","###########","\n\n")
    # print("DF : ", DF)
    # print("Term : ",Term)
    # print("Combos : ",combos)

    dfObj = pd.DataFrame(columns=['Related Term','Heading','Topic'])   
    
    for Heading in HeadingsPerTerm:
        for word in combos:
            result = findTopic(word,Heading)
            wordGroup = inflection.singularize(word)+","+inflection.pluralize(word)
            if result is not None:
                word,Heading = result
                dfObj = dfObj.append({'Related Term':Term,'Heading': Heading,'Topic':wordGroup}, ignore_index=True)
                
    print(dfObj)
    
          


def combifyData(DF):
   
    grouped_df = DF.groupby('Related Terms')
    DF.insert(3, "Topic","")# used in next function
    dataframes = []
    #print(DF)
    for key, item in grouped_df:
        relatedTerm = key
        texd = []
        #print(relatedTerm, "\n\n")
        for pages in item["Page"]:
            #print([d['PARAGRAPH'] for d in pages])
            texd.append([d['PARAGRAPH'] for d in pages])
        parasPerTerm = [i for sublist in texd for i in sublist]
        
        text = ' '.join(parasPerTerm)
        combos = combify(text, 1, stop_words=stopwords, limit=2)
        average = combos["NUMBER_OF_TIMES_FOUND"].mean() # calculate average
        average = average + 1

        df = combos[combos["NUMBER_OF_TIMES_FOUND"] > average] # Filter value less than average
        df= df.sort_values(by="NUMBER_OF_TIMES_FOUND", ascending=False) #Sort in Desc

        orderedCombos = tuple(list(df.index))
        createTopic(grouped_df.get_group(key),relatedTerm,orderedCombos)
        # dataframes.append(df)
        #print(orderedCombos)
    # with open('output.txt', 'w') as filehandle:
    #     for data in dataframes:
    #         filehandle.write('%s\n' % data)  
        
      
 

#Read CSV for URLs
df = pd.read_csv("Full.csv",index_col=False) 
#store relavant data
df=df[['URL','Related Terms']]

matchFrame = pd.read_csv("Plumbing Entities.csv",index_col=False)
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

#######################################################################################################################


combifyData(dfObj)