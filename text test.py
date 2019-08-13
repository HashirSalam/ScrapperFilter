import pandas as pd


post_text_file = open("shitballs.txt", "r")
post_text = ""

for words in post_text_file:
    post_text += words


def number_check(text):
    try:
        int(text)
        return True
    except:
        return False


text_list = [x for x in post_text.split("||")]
stored_number = 0
fin_article = {}
for line in text_list:
    if len(line.strip()) > 0:
        if number_check(line.strip()):
            stored_number = line
        else:
            fin_article[int(stored_number)-1] = line
            print(stored_number, line)
post_data = pd.DataFrame.from_dict(fin_article, orient='index', columns=["spun text"])
new_data = post_data[:]

combined = pd.concat([post_data, new_data], sort=False)
print(combined.head())

