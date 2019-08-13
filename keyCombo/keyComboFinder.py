import pandas as pd
from glob import glob
import os
import time
from concurrent.futures import ProcessPoolExecutor

now = time.time()


def archive_old_files(name, files):
    path = "Archive/"+name
    if not os.path.isdir(path):
        os.makedirs(path)
    for file in files:
        os.rename(file, path + "/" + file)


def get_entities_for_combos(combo_df, ents):
    ent_list = []
    for i in combo_df.index:
        ent_string = ""
        for ent in ents:
            if ent in i:
                ent_string += ent + ", "
        ent_list.append(ent_string)
    return ent_list


def combify(target, number, stop_words=[], dont_include=[], limit=int(0)):
    #print("starting combos " + str(number))
    text = target
    text = text.replace("-", ' ')
    text = text.replace("(", " ")
    text = text.replace(")", " ")
    text = text.translate(str.maketrans("", "", '",./@:;+=-()[]~!£$%^*`¬|?'))
    text = text.lower()
    text = text.replace("\n", " ")

    for word in stop_words:
        text = text.replace(" "+word+" ", " ")
    # remove all extra spaces
    starting_length = len(text)
    text = text.replace("  ", " ")
    # stop trying to remove spaces when the length stops changing
    while len(text) < starting_length:
        starting_length = len(text)
        text = text.replace("  ", " ")
    text = text.strip()
    # take text and split all words
    text_list = text.split(" ")
    for item in text_list:
        if len(item) == 0:
            print(item + "no length")
    # create a set of all combinations of 2 words
    combo_list = []
    for numbers in range(1, len(text_list)-number):
        # form the combo as a list
        combo = []
        combo.append(text_list[numbers])
        for repeat in range(1, number):
            new_index = numbers + repeat
            combo.append(text_list[new_index])
        # we assume the combo is good
        include = True
        # check if it's bad
        for wrd in combo:
            if wrd in dont_include:
                include = False
        # if its good
        if include:
            # form the combo as a string
            combi_string = ""
            for i in combo:
                combi_string += " " + i
            combi_string = combi_string.strip()
            combo_list.append(combi_string)
    #print("counting frequency for run number " + str(number))
    combo_dict = {}
    for each in combo_list:
        if len(each) > 2:
            combo_dict[each] = combo_dict.get(each, 0) + 1
        # output results
    df = pd.DataFrame.from_dict(combo_dict, orient="index")
    df.index.name = "COMBO"
    df["LENGTH OF COMBO"] = str(number)
    df.columns = ["NUMBER_OF_TIMES_FOUND", "LENGTH OF COMBO"]
    one_percent = df.max()["NUMBER_OF_TIMES_FOUND"]/100
    two_percent = one_percent+one_percent
    if limit > 0:
        df = df[df["NUMBER_OF_TIMES_FOUND"] > limit]
    if number == 1:
        df = df[df["NUMBER_OF_TIMES_FOUND"] > two_percent]

    return df

def JUST_DO_IT():
    now = time.time()
    targets = []
    for each in glob("input/*.txt"):
        targets.append(each)
    for targit in targets:
        frames = []
        print("combifying " + str(targit))
        numbers = [2, 3, 4, 5, 6, 7]
        with ProcessPoolExecutor(max_workers=6) as executor:
            dump = []
            for number in numbers:
                result = executor.submit(combify, targit, number)
                dump.append(result)
        for each in dump:
            frames.append(each.result())
        finalpath = "output/" + targit[5:-4] + ".csv"
        finshed_frame = pd.concat(frames)
        finshed_frame = finshed_frame.sort_values(by="NUMBER_OF_TIMES_FOUND", ascending=False)
        finshed_frame = finshed_frame[finshed_frame.NUMBER_OF_TIMES_FOUND != 1]
        finshed_frame = finshed_frame[finshed_frame.NUMBER_OF_TIMES_FOUND != 2]
        finshed_frame = finshed_frame.rename(columns={"NUMBER_OF_TIMES_FOUND": "NUMBER OF TIMES FOUND"})
        print(finshed_frame.head())
        finshed_frame.to_csv(finalpath, mode="w+")
        # put done files in the done folder
        move_path = targit[:6] + "completed/" + targit[6:]
        os.rename(targit, move_path)
        print("finished " + str(targit))
    print(str(time.time()-now), "seconds")


if __name__ == "__main__":
    JUST_DO_IT()

