import pandas as pd
from bs4 import BeautifulSoup as bs
from bs4 import Comment
import requests
import os
from keyCombo import ArchiveCleaner
import time
from bs4 import NavigableString


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
    for FUCKINGSHIT in soup("iframe"):
        FUCKINGSHIT.decompose()
    for noscript in soup("noscript"):
        noscript.decompose()
    for style in soup("style"):
        style.extract()
    for script in soup("script"):
        script.extract()
    for comments in soup.findAll(text=lambda text: isinstance(text, Comment)):
        comments.extract()
    for outbound_links in soup("a"):
        outbound_links.replace_with(outbound_links.text)
    try:
        h1 = soup.find("h1")
    except:
        h1 = soup.title


    if h1 == None:
        h1 = soup.title
    whole_fucking_page = []
    content_found = [h1]
    useful = []

    def GrabUseful(element):
        automatically_accept = ["h2", "h3", "h4", "h5", "h6", "p", "li"]
        if element.name in automatically_accept:
            return element
        else:
            if isinstance(element, NavigableString):
                return element.strip()

    ignore_next = False
    for element in h1.next_elements:
        whole_fucking_page.append(element)
    for i in whole_fucking_page:
        if ignore_next:
            ignore_next = False
        else:
            content_found.append(GrabUseful(i))
            if not isinstance(i, NavigableString):
                if i.name in ["h2", "h3", "h4", "h5", "h6", "p", "li"]:
                    ignore_next = True
    for item in content_found:
        if not item is None:
            useful.append(item)


    class TaggedItem:
        def __init__(self, input):
            if isinstance(input, NavigableString):
                self.name = "div"
                self.text = input.replace("\n", " ").replace("\t", " ")
            elif type(input) is str:
                self.name = "div"
                self.text = input.replace("\n", " ").replace("\t"," ")
            else:
                self.name = input.name
                self.text = input.text.replace("\n", " ").replace("\t"," ")
            tag_dict = {"title":1,"h1": 1, "h2": 2, "h3": 3, "h4": 4, "h5": 5, "h6": 6, "p": 7, "li": 7}
            if self.name == "div":
                self.value = 7
            else:
                self.value = tag_dict[self.name]
            self.text = ' '.join(self.text.split())


    listy = []

    for i in useful:
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
        df["Original URL"] = df["Original URL"].astype("category")
        df.h2 = df.h2.astype("category")
        df.h1 = df.h1.astype("category")
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
            if old[20:-4] == newline[7:]:
                successes.append(pd.read_csv(old,dtype={"Original URL":"category", "h1":"category",
                                                        "h2": "category",
                                                        "h3":"object",
                                                        "h4":"object",
                                                        "h5": "object",
                                                        "h6": "object",
                                                        "Data 1": "object",
                                                        }))
                print("found", newline, "in", old[20:])
                found_old = True
        if not found_old:
            if "pdf" not in line[-7:]:
                try:
                    successes.append(HeadingAndContentScrape(line))
                except:
                    print("failed ", str(line))
                    Fails.write(str(line) + "\n")
            else:
                report = str(line) + " has pdf in the final chars"
                print(report)
                Fails.write(report)
    Fails.close()
    if len(successes) > 0:
        result = pd.concat(successes)
        result["Original URL"] = result["Original URL"].str.lower()
    else:
        result = pd.DataFrame()
    return result

def GrabQuestions(url_list):
    sites = len(url_list)
    time_now = time.ctime()
    ArchiveCleaner.CleanUp("Failed Url Reports/",3)
    print("The time is now", time_now)
    print("Attempting to grab data from", sites, "sites", "\n")
    mins_to_go = (sites * 1.5)/60
    print("with a typical rate of 1.5 seconds per link that works out as ", mins_to_go, "minutes to go, see you soon!")
    df = ReportFails(url_list)
    ArchiveCleaner.ArchiveSize()
    temp_dict_list = []
    for row in df.iterrows():
        row = list(row[1])
        row.reverse()
        page_text = row[0]
        URL = row[-1:]
        row = row[1:-1]
        non_empty_heading = "No Heading Found"
        question_header = ""
        for each in row:
            each = str(each)
            if not each == "nan":
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
        temp_dict = {"Original URL": URL[0],"predicted question heading": question_header, "Data 1":page_text}
        temp_dict_list.append(temp_dict)
    temp_df = pd.DataFrame(temp_dict_list)
    return temp_df

GrabQuestions(["http://gardening.jhbandeastrand.co.za/areas/garden-services-kagiso/"])
#ALL_LINKS.close()
