import pandas as pd
from bs4 import BeautifulSoup as bs
import requests
import os
from keyCombo import ArchiveCleaner
import time


def check_for_q(words):
    if "?" in words:
        return True
    words = words.lower()
    q_words = ["how ", "what ", "who ", "when ", "does ", "can ", "vs ", "versus "]
    for each in q_words:
        if words.startswith(each):
            return True
        if " " + each in words:
            return True


def HeadingAndContentScrape(link):
    """

    @:param link:
    :return scraped content:
    """

    user = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    agent = "(KHTML, like Gecko) Chrome/74.0.3729.108 Safari / 537.36"
    user_agent = user + agent

    poop = requests.get(link, headers={'User-Agent': user_agent}, timeout=5)

    headers = ["h1", "h2", "h3", "h4", "h5", "h6", "p", "li"]

    soup = bs(poop.text, 'html5lib')

    try:
        h1 = soup.find("h1")
    except:
        h1 = soup.title

    if h1 == None:
        h1 = soup.title

    useful = soup.title.find_all_next(headers)


    class TaggedItem:
        def __init__(self, input):
            self.name = input.name
            self.text = input.text.replace("\n", " ").replace("\t"," ")
            tag_dict = {"h1": 1, "h2": 2, "h3": 3, "h4": 4, "h5": 5, "h6": 6, "p": 7, "li": 7}
            self.value = tag_dict[self.name]
            if self.name == "div":
                if len(self.text.strip()) > 5:
                    self.value = 7

    listy = []

    for i in useful:
        print(i)
        items = TaggedItem(i)
        listy.append(items)

    h2, h3, h4, h5, h6, text = "", "", "", "", "", ""

    def InsertInList(list, item):
        list = list[:item.value]
        empty = 6 - item.value
        list.append(item.text)
        while empty > 0:
            empty -= 1
            list.append("")
        return list

    if len(listy) > 3:
        previous_term = listy[0]
        tags = [link, h1.text.strip(), h2, h3, h4, h5, h6, text]
        page = [tags]
        for item in listy[1:]:
            if len(item.text.strip()) > 2:
                if item.value <= previous_term.value:
                    page.append(tags)
                tags = InsertInList(tags, item)
            previous_term = item

        df = pd.DataFrame(page)
        df.columns = ["Original URL", "h1", "h2", "h3", "h4", "h5", "h6", 'Data 1']
        destination = link[7:].replace("/","-")
        destination = destination.replace(".", "-")
        destination = destination.replace("=", "")
        destination = destination.replace("?", "")
        if len(destination) > 120:
            destination = destination[:120]
        if not os.path.isdir("Archive/Raw Scrapes"):
            os.makedirs("Archive/Raw Scrapes")
        destination = "Archive/Raw Scrapes/" + destination + ".csv"
        df.to_csv(destination, index=False)
        return df


# link_list = []
# ALL_LINKS = open("links.txt", "r", encoding="utf8")
#
# for line in ALL_LINKS:
#     link_list.append(line)
# first_fucker = link_list[0]
# first_fucker = first_fucker[1:]
# link_list = link_list[1:]
# link_list.append(first_fucker)


def ReportFails(list_of_urls):
    successes = []
    print("Cleaning Archive...")
    current_archive = ArchiveCleaner.CleanUp()
    time_now = time.ctime()
    fail_name = "Failed Url Reports/Failed url report " + str(time_now).replace(":", "-") + ".txt"
    Fails = open(fail_name, "w+")
    print("Grabbing Data...")
    for line in list_of_urls:
        line = line.strip("ï»¿")
        line = line.strip("\n")
        newline = line.replace(".", "-")
        newline = newline.replace("/", "-")
        newline = newline.replace("=", "")
        newline = newline.replace("?", "")
        found_old = False
        for old in current_archive:
            if old[20:-4] in newline:
                successes.append(pd.read_csv(old))
                print("found", newline, "in", old[20:])
                found_old = True
        if not found_old:
            if "pdf" not in line[-7:]:
                try:
                    successes.append(HeadingAndContentScrape(line))
                except:
                    print("failed ", str(line))
                    Fails.write(str(line))
            else:
                report = str(line) + " has pdf in the final chars"
                print(report)
                Fails.write(report)
    Fails.close()
    if len(successes) > 0:
        result = pd.concat(successes)
    else:
        result = pd.DataFrame()
    return result

def GrabQuestions(url_list):
    sites = len(url_list)
    time_now = time.ctime()
    print("The time is now", time_now)
    print("Attempting to grab data from", sites, "sites", "\n")
    mins_to_go = (sites * 1.5)/60
    print("with a typical rate of 1.5 seconds per link that works out as ", mins_to_go, "minutes to go, see you soon!")
    df = ReportFails(url_list)
    ArchiveCleaner.CleanUp()
    df.fillna("", inplace=True)
    temp_dict_list = []
    for row in df.iterrows():
        row = list(row[1])
        row.reverse()
        page_text = row[0]
        row = row[1:]
        non_empty_heading = ""
        question_header = ""
        for each in row:
            each = str(each)
            if len(each)>0:
                non_empty_heading = each
                break
                print(non_empty_heading)
        for each in row:
            if type(each) is str:
                if check_for_q(each):
                    question_header = each
                    break
        if len(question_header) == 0:
            question_header = non_empty_heading
        temp_dict = {"Original URL": row[6],"predicted question heading": question_header, "Data 1":page_text}
        temp_dict_list.append(temp_dict)
    temp_df = pd.DataFrame(temp_dict_list)
    return temp_df



#ALL_LINKS.close()

