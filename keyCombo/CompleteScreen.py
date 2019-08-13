import time
from time import sleep



def FinishedSheet(name, time_started):
    print("------------------------------------------")
    print("------------------------------------------")
    print("WOW, we finished the", name, "sheet!")
    thumb="            _\n"\
        "          /(|\n"\
        "         (  :\n"\
        "        __\  \  _____\n"\
        "       (____)  `|\n"\
        "      (____)|   |\n"\
        "       (____).__|\n"\
        "        (___)__.|_____\n"
    print(thumb)
    finish_time = time.time()
    time_taken = finish_time-time_started
    print("that only took", time_taken, "seconds!", "\n")
    print("------------------------------------------", "\n")
    mins_taken = time_taken/60
    print("that's a mere",mins_taken, "minutes!")
    print("------------------------------------------")
    print("------------------------------------------")

