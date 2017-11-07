import json 
import requests
import time
import wget
from watson_developer_cloud import NaturalLanguageClassifierV1



TOKEN = ""
URL = "https://api.telegram.org/bot{}/".format(TOKEN)

def watson(text):
    natural_language_classifier = NaturalLanguageClassifierV1(
        username='5b314083-6286-4ad6-86b0-c6d0ea4aa266',
        password='')

    response = natural_language_classifier.classify('1e0d8ex232-nlc-26798', text)['top_class']
    return(str(response))


def getUrl(url):
    response = requests.get(url)
    content = response.content.decode("utf8")
    return content


def downloadUrl(url):
    wget.download(url,out='asd.jpg')
    print('\n')


def jsonFromUrl(url):
	content = getUrl(url)
	js = json.loads(content)
	return js



def getUpdates(offset=None):
	url = URL + "getUpdates?timeout=100"
	if offset:
		url += '&offset={}'.format(offset)
	js = jsonFromUrl(url)
	return js


def lastChatIdText(updates):
	num_updates = len(updates["result"])
	last_update = num_updates - 1
	text = updates["result"][last_update]["message"]["text"]
	chat_id = updates["result"][last_update]["message"]["chat"]["id"]
	return (text, chat_id)


def sendMessage(text, chat_id):
	text = urllib.parse.quote_plus(text)
	url = URL + "sendMessage?text={}&chat_id={}".format(text, chat_id)
	getUrl(url)


def getLastUpdateId(updates):
    update_ids = []
    for update in updates["result"]:
        update_ids.append(int(update["update_id"]))
    return max(update_ids)

def getLastUpdate(updates):
    update_ids = []
    for update in updates["result"]:
        update_ids.append(int(update["update_id"]))
    for i in updates['result']:
        if i['update_id'] == max(update_ids):
            return i



def echoAll(updates):
	for update in updates["result"]:
		text = update["message"]["text"]
	chat = update["message"]["chat"]["id"]
	sendMessage(text, chat)




def getFile(file_id):
    json = jsonFromUrl(URL + 'getFile?file_id={}'.format(file_id))
    downloadUrl('https://api.telegram.org/file/bot{}/{}'.format(TOKEN, json['result']['file_path']))


def getFileId(resolution):
    updates = getUpdates()
    file_id = ''
    greatest = 0
    least = 20000001
    for j,i in enumerate(updates['result']):
        if i['update_id'] == getLastUpdateId(updates):
            path = updates['result'][j]['message']['photo']
            break
    if resolution:
        for i in path:
            if i['file_size'] > greatest:
                greatest = i['file_size']
        for i in path:
            if i['file_size'] == greatest:
                return i['file_id']
    else:
        for i in path:
            if i['file_size'] < greatest:
                greatest = i['file_size']
        for i in path:
            if i['file_size'] == greatest:
                 return i['file_id']


def getMessageType(dictionary):
    if 'caption' in dictionary:
        return 'caption'
    elif 'photo' in dictionary:
        return 'photo'
    elif 'text' in dictionary:
        return 'text'

def main():
    last_message = getLastUpdate(getUpdates())
    last_message_type = getMessageType(last_message)
    if last_message_type == 'text':
        print(watson(last_message['text']))


if __name__ == '__main__':
    main()

