import json 
import requests
import time
import wget
from watson_developer_cloud import NaturalLanguageClassifierV1
import telegram
import os

os.chdir(os.environ['HOME']  + '/ibm_watson')	

lxybot = telegram.Bot("386957960:AAH63k5bZW3ONF4ZdDcVYdmHEXO9HhdmpQY")

TOKEN = "386957960:AAH63k5bZW3ONF4ZdDcVYdmHEXO9HhdmpQY"
URL = "https://api.telegram.org/bot{}/".format(TOKEN)

def watson(text):
    natural_language_classifier = NaturalLanguageClassifierV1(
        username='5b314083-6286-4ad6-86b0-c6d0ea4aa266',
        password='mawh434bmDVG')

    response = natural_language_classifier.classify('1e0d8ex232-nlc-26798', text)['top_class']
    return(str(response))


def getUrl(url):
    response = requests.get(url)
    content = response.content.decode("utf8")
    return content


def downloadUrl(url, name):
    wget.download(url,out=name)
    print('\n')


def jsonFromUrl(url):
	content = getUrl(url)
	js = json.loads(content)
	return js



def getUpdates(offset=None):
	url = URL + "getUpdates?timeout=100&alllowed_updates=['message']"
	if offset:
		url += '&offset={}'.format(offset)
	js = jsonFromUrl(url)
	return js


def lastChatIdText(updates):
	num_updates = len(updates["result"])
	last_update = num_updates - 1
	try:
		text = updates["result"][last_update]["message"]["text"]
	except:
		try:
			text = updates["result"][last_update]["message"]["edited_text"]
		except:
			raise Exception('Ei ole viesti')
	chat_id = updates["result"][last_update]["message"]["chat"]["id"]
	return [text, chat_id]


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
	if len(updates['result']) == 0:
		raise Exception('No messages yet')
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




def getFile(file_id, path):
	json = jsonFromUrl(URL + 'getFile?file_id={}'.format(file_id))
	url = 'https://api.telegram.org/file/bot{}/{}'.format( TOKEN, json['result']['file_path'])
	downloadUrl(url, path)


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

def sendImage(chat_id, path, caption=''):
	lxybot.send_photo(chat_id=chat_id, photo=open(path, 'rb'), caption=caption)
	
def getChatTitle(update):
	if update['message']['chat']['type'] == 'group':
		print(update['message']['chat']['type'])
		print(update)
		return update['message']['chat']['title']
	elif update['message']['chat']['type'] == 'private':
		print(update['message']['chat']['type'])
		print(update)
		return update['message']['chat']['first_name']
	else:
		print('virhe')
	
	
	

def main():
	last_message_before = None
	while True:
		#print(getUpdates())
		last_message = getLastUpdate(getUpdates())
		try:
			last_message_type = getMessageType(last_message['message'])
			last_message_content = last_message['message']
		except KeyError:
			try:
				last_message_type = getMessageType(last_message['edited_message'])
				last_message_content = last_message['edited_message']
			except:
				raise Exception('Ei ole viesti')
		#print(getChatTitle())
		
		"""print(getLastUpdate(getUpdates()))
		print(last_message_content['text']ts)"""

		if last_message != last_message_before: 
			print('Uusi viesti:')
			last_title = getChatTitle(last_message)
			print(last_title)
			if last_message_type == 'text' and'@' in last_message_content['text']:
				print(last_message_content['text'])
				chat_id = lastChatIdText(getUpdates())[1]
				kouluaine = watson(last_message_content['text'])
				print(last_title)
				path = os.environ['HOME'] + '/ibm_watson/{}/{}.jpg'.format(last_title, kouluaine)
				print(path)
				print(kouluaine)
				sendImage(chat_id, path, 'olepahyvä')
				print(watson(last_message_content['text']))
				
			elif last_message_type == 'caption' and '@' in last_message_content['caption']: 
				caption = last_message['message']['caption']
				print(caption)
				kouluaine = watson(caption)
				print(not os.path.isdir('./{}'.format(last_title)))
				print(os.path.isfile('{}/{}.jpg'.format(last_title, kouluaine)))
				if not os.path.isdir('./{}'.format(last_title)):
					os.mkdir('./{}'.format(last_title))
				if os.path.isfile('{}/{}.jpg'.format(last_title, kouluaine)):
					os.remove('{}/{}.jpg'.format(last_title, kouluaine))
				getFile(getFileId(1), './{}/{}.jpg'.format(last_title, kouluaine))
		last_message_before = last_message
	print(last_message)
	print('text' in last_message['message'])
	#print(lastChatIdText(getUpdates()))
	#print(lastChatIdText(getUpdates())[1])
	#sendImage(lastChatIdText(getUpdates())[1])
	last_message_before = last_message
	

	
if __name__ == '__main__':
    main()

