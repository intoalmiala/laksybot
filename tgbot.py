import json 
import requests
import time
import urllib

TOKEN = "459820092:AAHoQ5rCgtTWWRspi6dNQKHeuB3EHBqeCqM"
URL = "https://api.telegram.org/bot{}/".format(TOKEN)


def getUrl(url):
	response = requests.get(url)
	content = response.content.decode("utf8")
	return content

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

def echoAll(updates):
	for update in updates["result"]:
		text = update["message"]["text"]
	chat = update["message"]["chat"]["id"]
	sendMessage(text, chat)

def getFile(file_id):
    json = jsonFromUrl(URL + 'getFile?file_id={}'.format(file_id))
    getUrl('api.telegram.org/file/bot{}/{}'.format(TOKEN, json['file_path']))

def main():
    getFile(getUpdates()['result'][0]['message']['photo'][0]['file:id'])
    """while True:
	    sendMessage('moi', 293275065)"""

if __name__ == '__main__':
	main()

