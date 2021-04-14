#!/usr/bin/env python3

from tinydb import TinyDB
import requests
import sys
import re
import os	


API_KEY = ''
db = TinyDB('./uploaded.json')
uploadedDict = {}

# Change this with path up hs/ directory. Can also be just a file
# If left None the script expects the first argument to be a file/directory to upload
folder = None

upload_page = "https://amsterdamhome.ddns.net:8888/uploadfile"

# Regex for upload codes
upload_error_re = re.compile("File already exists")
upload_success_re = re.compile("Upload Success")
upload_duplicate_re = re.compile("<div style='color:OrangeRed'>(.*?)</div>")

# Files to be uploaded
files = []


def fatal(s):
    error(s)
    sys.exit(-1)


def error(s):
    print('\033[31m' + s + '\033[0m', file=sys.stderr)


def success(s):
    print('\033[32m' + s + '\033[0m')

def initDB():
    for line in db.all():
        name = line['n']
        yes = line['y']
        uploadedDict[name] = yes

def send_file(file_name):
    if file_name in uploadedDict:
        error("File is already uploaded %s" % (file_name))
        return

    with open(folder+'/'+file_name, "rb") as fd:
        
        cookies = {'token':API_KEY}
        ret = requests.post(upload_page, files={"filename": fd}, cookies=cookies)

        if int(ret.status_code) != 200:
            fatal("Error code %s at upload!" % str(ret.status_code))

        # Turn returned text into a oneline for easy regex match
        one_line = re.sub(r"[\n\t\r]*", "", ret.text)

        match = upload_error_re.search(one_line)

        if match is not None:
            error("Error uploading %s" % (file_name))
            return

        match = upload_duplicate_re.search(one_line)

        if match is not None:
            error("File is duplicate %s" % (file_name))
            uploadedDict[file_name] = 'yes'
            entry = {}
            entry['n'] = str(file_name)
            entry['y'] = str('yes')
            db.insert(entry)
            return

        match = upload_success_re.search(one_line)

        if match is not None:
            uploadedDict[file_name] = 'yes'
            entry = {}
            entry['n'] = str(file_name)
            entry['y'] = str('yes')
            db.insert(entry)
            success(file_name+" uploaded successfully!")
            # Uncomment if you want to delete file after upload
            # os.remove(folder+'/'+file_name)
            return

        fatal("Unspecified error: %s" % ret.text)


if folder is None:
    if len(sys.argv) < 2:
        fatal("Use with %s <capture/capture_folder>" % sys.argv[0])
    folder = sys.argv[1]

if os.path.isdir(folder):
    files = [f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))]
    print("You are about to send:")
    for file in files:
        print(file)
    sys.stdout.write("Please confirm (y/n):")
    sys.stdout.flush()
    text = input()
    if text.lower()[0] != 'y':
        sys.exit(0)
elif os.path.isfile(folder):
    files.append(folder)
else:
    fatal("File/folder %s does not exist" % folder)

initDB()
# Upload file one by one so we minimize amount of max_size errors
for file in files:
    send_file(file)