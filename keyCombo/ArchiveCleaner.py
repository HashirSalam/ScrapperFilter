import os
import glob
import time

def convert_bytes(num):
    """
    this function will convert bytes to MB.... GB... etc
    """
    for x in ['bytes', 'KB', 'MB', 'GB', 'TB']:
        if num < 1024.0:
            return "%3.1f %s" % (num, x)
        num /= 1024.0

def ArchiveSize(location = "Archive/Raw Scrapes/"):
    if os.path.isdir(location):
        size = os.path.getsize(location)
        nice_size = convert_bytes(size)
        print("\nThe Raw Scrapes in the Archive currently contains", nice_size, "of data.\n")

def CleanUp(location = "Archive/Raw Scrapes/", days = 30):
    path = "Failed Url Reports/"
    if not os.path.isdir(path):
        os.makedirs(path)
    path += "*"
    failed_urls = glob.glob(path)
    for txt in failed_urls:
        if os.path.getsize(txt) < 1:
            os.remove(txt)
    archived_scrapes = glob.glob(location+"*")
    for each in archived_scrapes:
        creation = os.path.getctime(each)
        time_elapsed = time.time() - creation
        seconds_in_30_days = 60*60*24*days
        if time_elapsed > seconds_in_30_days:
            print(each, "is older than", days, "days, deleting...\n")
            os.remove(each)
    updated_archive = glob.glob(location+"*")
    if location == "Archive/Raw Scrapes/":
        ArchiveSize(location)
    return updated_archive

