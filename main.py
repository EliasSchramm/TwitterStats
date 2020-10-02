import requests
import os
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
import time
from datetime import datetime
import threading
from collections import OrderedDict
from emoji import UNICODE_EMOJI

webServer = 0
hostName = "localhost"
serverPort = 80
website = ""
startTime = 0
currentTime = 0
lastMin = -1
startMin = 0;

# Stats

lastTweet = ""
countTweets = 0
countReTweets = 0
countHashtags = 0
countTags = 0
countEmoji = 0

back_hashtags = dict()
for_hashtags = dict()

mins_hashtags = dict()
mins_emoji = dict()
mins_tag = dict()

back_tag = dict()
for_tag = dict()

back_emoji = dict()
for_emoji = dict()


class MyServer(BaseHTTPRequestHandler):
    def do_GET(self):
        global website, lastTweet, currentTime

        getWebsite("index.html")

        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

        website_copy = website
        currentTime = int(time.time())

        top20 = ""
        top20t = ""
        top20e = ""
        i = 0

        for k, v in for_hashtags.items():
            i += 1
            top20 += '"' + str(k) + '" : ' + str(v) + '<br>'
            if i >= 20:
                break

        i = 0

        for k, v in for_tag.items():
            i += 1
            top20t += '"' + str(k) + '" : ' + str(v) + '<br>'
            if i >= 20:
                break

        i = 0

        for k, v in for_emoji.items():
            i += 1
            top20e += '"' + str(k) + '" : ' + str(v) + '<br>'
            if i >= 20:
                break

        website_copy = website_copy.replace("$lastTweet$", lastTweet)
        website_copy = website_copy.replace("$upTime$", str(int(getCurrentDelta() / 60)))
        website_copy = website_copy.replace("$num_tweets$", str(countTweets))
        website_copy = website_copy.replace("$num_re_tweets$", str(countReTweets))
        website_copy = website_copy.replace("$num_hashtags$", str(countHashtags))
        website_copy = website_copy.replace("$num_emoji$", str(countEmoji))
        website_copy = website_copy.replace("$num_tag$", str(countTags))
        website_copy = website_copy.replace("$top20Hashtags$", top20)
        website_copy = website_copy.replace("$top20tag$", top20t)
        website_copy = website_copy.replace("$top20emoji$", top20e)

        for line in website_copy.split("\n"):
            self.wfile.write(
                bytes(line + "\n", "utf-8"))


def getCurrentDelta():
    return int((currentTime - startTime) / 60)


def getWebsite(url):
    global website

    f = open(url, "r")
    website = f.read()
    f.close()


def runServer():
    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass


def handleTweet(tweet):
    global countReTweets, countTweets, lastTweet, back_hashtags, countHashtags, countTags, countEmoji, back_emoji
    # ReTweets will get Ignored

    if not tweet.startswith("RT"):
        lastTweet = tweet
        words = tweet.split(" ")

        for word in words:
            if word.startswith("#"):
                addToCurrentMinute("hashtag", word)
                countHashtags += 1

                if word in back_hashtags:
                    back_hashtags[word] = back_hashtags[word] + 1
                else:
                    back_hashtags[word] = 1
            elif word.startswith('@') and not word == "@":
                addToCurrentMinute("tag", word)
                countTags += 1

                if word in back_tag:
                    back_tag[word] = back_tag[word] + 1
                else:
                    back_tag[word] = 1
            else:
                chars = word.split()
                for char in chars:
                    if char in UNICODE_EMOJI.keys():
                        addToCurrentMinute("emoji", char)
                        countEmoji += 1
                        if char in back_emoji:
                            back_emoji[char] = back_emoji[char] + 1
                        else:
                            back_emoji[char] = 1


    else:
        countReTweets += 1

    countTweets += 1


def auth():
    return "AAAAAAAAAAAAAAAAAAAAAD0MGwEAAAAA9bKsrZqMy%2FbuPSgEHGWObQV7itU%3DeGbT5B29p19id5aOHwkUFPpc4EpAXvcDbGWdKYg5OgsFSqdn7c"


def create_url():
    return "https://api.twitter.com/2/tweets/sample/stream"


def create_headers(bearer_token):
    headers = {"Authorization": "Bearer {}".format(bearer_token)}
    return headers


def connect_to_endpoint(url, headers):
    response = requests.request("GET", url, headers=headers, stream=True)

    for response_line in response.iter_lines():
        if response_line:
            json_response = json.loads(response_line)
            threading.Thread(target=handleTweet, args=(json_response["data"]["text"],)).start()

    if response.status_code != 200:
        raise Exception(
            "Request returned an error: {} {}".format(
                response.status_code, response.text
            )
        )


def main():
    global currentTime
    bearer_token = auth()
    url = create_url()
    headers = create_headers(bearer_token)
    timeout = 0
    x = threading.Thread(target=runServer)
    x.start()
    xx = threading.Thread(target=updateDicts)
    xx.start()

    print("Server started http://%s:%s" % (hostName, serverPort))

    while True:
        connect_to_endpoint(url, headers)
        timeout += 1


def addToCurrentMinute(type, content):
    now = datetime.now()
    if type == "hashtag":
        if content in mins_hashtags[lastMin]:
            mins_hashtags[lastMin][content] = mins_hashtags[lastMin][content] + 1
        else:
            mins_hashtags[lastMin][content] = 1

    elif type == "emoji":
        if content in mins_emoji[lastMin]:
            mins_emoji[lastMin][content] = mins_emoji[lastMin][content] + 1
        else:
            mins_emoji[lastMin][content] = 1
    else:
        if content in mins_tag[lastMin]:
            mins_tag[lastMin][content] = mins_tag[lastMin][content] + 1
        else:
            mins_tag[lastMin][content] = 1


def updateDicts():
    global back_hashtags, for_hashtags, for_tag, for_emoji, now, lastMin
    while True:
        for_hashtags = OrderedDict(sorted(back_hashtags.items(), key=lambda x: x[1], reverse=True))
        for_tag = OrderedDict(sorted(back_tag.items(), key=lambda x: x[1], reverse=True))
        for_emoji = OrderedDict(sorted(back_emoji.items(), key=lambda x: x[1], reverse=True))

        now = datetime.now()

        if now.minute != lastMin:
            lastMin = now.minute

            rem = 0

            for k, v in mins_hashtags[now.minute].items():
                back_hashtags[k] = back_hashtags[k] - v
                rem += 1
                if back_hashtags[k] < 0:
                    back_hashtags[k] = 0

            print(str(rem) + " hashtags korrigiert")

            rem = 0
            for k, v in mins_tag[now.minute].items():
                back_tag[k] = back_tag[k] - v
                rem += 1
                if back_tag[k] < 0:
                    back_tag[k] = 0

            print(str(rem) + " tags korrigiert")

            for k, v in mins_emoji[now.minute].items():
                back_emoji[k] = back_emoji[k] - v
                if back_emoji[k] < 0:
                    back_emoji[k] = 0

            mins_emoji[now.minute] = dict()
            mins_tag[now.minute] = dict()
            mins_hashtags[now.minute] = dict()

            print("Min reset " + str(now.minute))

        time.sleep(1)


if __name__ == "__main__":
    webServer = HTTPServer((hostName, serverPort), MyServer)
    getWebsite("index.html")
    startTime = int(time.time())

    now = datetime.now()

    lastMin = now.minute

    for i in range(0, 60):
        mins_tag[i] = dict()
        mins_hashtags[i] = dict()
        mins_emoji[i] = dict()

    main()
