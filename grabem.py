from bs4 import BeautifulSoup as bs
import requests
import pandas as pd
from keyCombo.keyComboFinder import combify
from keyCombo.comboData import stopwords
from spinrewriter import SpinRewriter
rewriter = SpinRewriter('info@sussexseo.net', '82109b0#51de401_45b0364?5ada2fd')


def number_check(text):
    try:
        int(text)
        return True
    except:
        return False


def rev_len(x):
    return -len(x)


def combo_counter(combos, paragraph):
    count = 0
    original_len = len(paragraph)
    combos.sort(key=rev_len)
    for each in combos:
        como_length = len(each)
        para_len = len(paragraph)
        paragraph = paragraph.replace(each, "")
        new_len = len(paragraph)
        change_in = para_len - new_len
        found = change_in/como_length
        count += found
    return count


def topic_binner(topic_column):
    if type(topic_column) is str:
        if len(topic_column) > 1:
            return True
    return False


def useful_para(useful, paragraph):
    if len(paragraph) < 51:
        return False
    for combination in useful:
        if combination in paragraph:
            return True
    return False


def smash_and_grab(link):
    user = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    agent = "(KHTML, like Gecko) Chrome/74.0.3729.108 Safari / 537.36"
    user_agent = user + agent

    poop = requests.get(link, headers={'User-Agent': user_agent}, timeout=10)

    headers = ["h1", "h2", "h3", "h4", "h5", "h6"]
    soup = bs(poop.text, 'html5lib')
    for outbound_links in soup("a"):
        outbound_links.replace_with(outbound_links.text)

    try:
        h1 = soup.find("h1")
    except:
        h1 = soup.title

    if h1 is None:
        h1 = soup.title

    page = []

    if h1 is not None:
        little_dict = {"header": h1.text, "url": link}
        grab = True
        for each in h1.next_elements:
            if each.name in headers:
                grab = True
                little_dict["header"] = each.text.strip()
            elif grab:
                if each.name is "p":
                    grab = False
                    little_dict["first line"] = each.text.strip()
                    page.append(little_dict)
                    little_dict = {"url": link}
    df = pd.DataFrame(page)
    return df


def all_data(list_of_links):
    dataframes = []
    for link in list_of_links:
        try:
            dataframes.append(smash_and_grab(link))
        except:
            print("failed to grab", link)
    df = pd.concat(dataframes, ignore_index=True)
    print("grabbed data")
    df = df[["url", "header", "first line"]]
    headings = ""
    for head in df["header"]:
        headings += head
    most_words = combify(headings, 1, stopwords)
    most_words.sort_values(by="NUMBER_OF_TIMES_FOUND", inplace=True, ascending=False)
    topics = []
    for i in df.index:
        head_to_check = df.at[i, "header"]
        small_dict = {"header": head_to_check}
        word_list = list(most_words.index)
        for word in word_list:
            if word in head_to_check.lower():
                small_dict["First topic word"] = word
                word_list.pop(word_list.index(word))
                break
        for word in word_list:
            if word in head_to_check.lower():
                small_dict["Second topic word"] = word
                word_list.pop(word_list.index(word))
                break
        if "Second topic word" not in small_dict.keys():
            small_dict["Second topic word"] = ""
        for word in word_list:
            if word in head_to_check.lower():
                small_dict["Third topic word"] = word
                word_list.pop(word_list.index(word))
                break
        if "Third topic word" not in small_dict.keys():
            small_dict["Third topic word"] = ""
        for q in ["how", "what", "who", "where", "when"]:
            if q in head_to_check.lower():
                small_dict["Q word"] = q
        if "Q word" not in small_dict.keys():
            small_dict["Q word"] = ""
        topics.append(small_dict)
    topics_info = pd.DataFrame(topics)
    topics_info = topics_info[["header", "First topic word", "Second topic word", "Third topic word", "Q word"]]
    print(topics_info.head(10))
    df = pd.merge(df, topics_info, on="header", left_index=True, right_index=True, how="right")
    print(df.head())
    texd = ""
    for words in df["first line"]:
        words = words.strip()
        texd += words
    combos = combify(texd, 1, stop_words=stopwords, limit=2)
    combos.to_csv("Combo output for thingy for MTD.csv")
    useful_combos = {}
    for combination in combos.index:
        useful_combos[combination] = combos.at[combination, "NUMBER_OF_TIMES_FOUND"]
    df["BIN"] = "Bin"
    for topics in ["First topic word", "Second topic word", "Third topic word"]:
        for i in df.index:
            if topic_binner(df.at[i, topics]):
                df.at[i, "BIN"] = "keep"
    df = df[df["BIN"] == "keep"]
    df = df[[useful_para(useful_combos, x) for x in df["first line"]]]
    df["head topics"] = df["First topic word"] + df["Second topic word"] + df["Third topic word"]
    df.drop(columns="BIN", inplace=True)
    como_list = [x for x in useful_combos.keys()]
    df["score"] = [combo_counter(como_list, x)for x in df["first line"]]
    topic_scores = {}
    for i in df.index:
        head_t = df.at[i, "head topics"]
        score = df.at[i, "score"]
        if head_t in topic_scores:
            if score > topic_scores[head_t]["score"]:
                topic_scores[head_t]["score"] = score
                topic_scores[head_t]["heading"] = df.at[i, "header"]
                topic_scores[head_t]["paragraph"] = df.at[i, "first line"]
        else:
            topic_scores[head_t] = {}
            topic_scores[head_t]["topic"] = head_t
            topic_scores[head_t]["score"] = score
            topic_scores[head_t]["heading"] = df.at[i, "header"]
            topic_scores[head_t]["paragraph"] = df.at[i, "first line"]
    article = pd.DataFrame.from_dict(topic_scores, "index")
    article.replace("\d+", "", True, regex=True)
    article.replace("\£", "", True, regex=True)
    article.sort_values(by="score", inplace=True, ascending=False)
    article = article.head(30)
    article = article.reset_index()
    article.to_csv("Output for thingy for MTD.csv", index=False)
    text = ""
    count = 1
    for each in article["paragraph"]:
        addition = "||" + str(count) + "|| "
        text += addition
        como_list.append(addition)
        count += 1
        text += each + "\n"
    shit_balls = open("shitballs.txt", "w+")
    shit_balls.write(text)
    shit_balls.close()
    shittier_balls = open("shittier balls.txt", "w+")
    response = rewriter.api._transform_plain_text('unique_variation', text, como_list, 'high')
    shittier_balls.write(response["response"])
    shittier_balls.close()
    post_text = response["response"]

    text_list = [x for x in post_text.split("||")]
    stored_number = 0
    fin_article = {}
    for line in text_list:
        if len(line.strip()) > 0:
            if number_check(line.strip()):
                stored_number = line
            else:
                fin_article[int(stored_number) - 1] = line
                print(stored_number, line)
    post_data = pd.DataFrame.from_dict(fin_article, orient='index', columns=["spun text"])
    output = article.merge(post_data, left_index=True, right_index=True)
    output.to_csv("FINISHeD THING.csv", index=False)




file = open("Olly.txt", "r", encoding="utf8")
links = []
for line in file:
    text = line.strip()
    if len(text) > 0:
        links.append(text)

all_data(links)

