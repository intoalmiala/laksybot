import json 
import requests
import time
import wget
from watson_developer_cloud import NaturalLanguageClassifierV1
import telegram
import os
import urllib

os.chdir(os.environ['HOME']  + '/laksybot')	




TOKEN = "" #This is for the authentication of the bot.
lxybot = telegram.Bot(TOKEN)
URL = "https://api.telegram.org/bot{}/".format(TOKEN)

def watson(text): #This function deternies, which school subject is being talked about in the input string.
    natural_language_classifier = NaturalLanguageClassifierV1(
        username='5b314083-6286-4ad6-86b0-c6d0ea4aa266',
        password='')

    response = natural_language_classifier.classify('1e0d8ex232-nlc-26798', text)['top_class']
    return(str(response))


def getUrl(url): # Opens an url
    response = requests.get(url)
    content = response.content.decode("utf8")
    return content


def downloadUrl(url, name): #Downloads the contents of the input url.
    wget.download(url,out=name)
    print('\n')


def jsonFromUrl(url): #Returns a json object from the contents of a given url.
	content = getUrl(url)
	js = json.loads(content)
	return js


update_counter = 0

def getUpdates(): # Returns a JSON object representing the events that occur during interacting with the bot.
    url = URL + "getUpdates?timeout=100&alllowed_updates=['message']"
    if update_counter > 90:
        return getUpdatesWithOffset(getLastUpdateId(getUpdatesWithOffset()))
    js = jsonFromUrl(url)
    return js


def getUpdatesWithOffset(offset=None):
    url = URL + "getUpdates?timeout=100&alllowed_updates=['message']&offset={}".format(offset)
    js = jsonFromUrl(url)
    return js


def lastChatIdText(updates): # Returns the last chat id that is being used in distinguishing between the homework of different groups.
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
    
def lastSenderId(update):
    if update['message']['chat']['type'] == 'group':
        print('group')
        print(update['message']['chat']['id'])
        return update['message']['chat']['id']
    if update['message']['chat']['type'] == 'private':
        print('private')
        print(update['message']['from']['id'])
        return update['message']['from']['id']


def sendMessage(text, chat_id): #Sends a message to a given chat_id.
    text = urllib.parse.quote_plus(text)
    url = URL + "sendMessage?text={}&chat_id={}".format(text, chat_id)
    print('Lähetin viestin: {} {}:lle'.format(text, chat_id))
    getUrl(url)


def getLastUpdateId(updates): #Gets the highest id, and thus last, id from the JSON object that is returned by the getUpdates function.
    update_ids = []
    for update in updates["result"]:
        update_ids.append(int(update["update_id"]))
    return max(update_ids)

def getLastUpdate(updates): # Returns the last event that is visible in the getUpdates JSON object.
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

def getFile(file_id, path): #Downloads an image from telegram servers specified by an image id. path is the location that the image is going to be saved to.
    json = jsonFromUrl(URL + 'getFile?file_id={}'.format(file_id))
    url = 'https://api.telegram.org/file/bot{}/{}'.format( TOKEN, json['result']['file_path'])
    downloadUrl(url, path)


def getFileId(resolution): # Gets the id of the best-quality image.
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


def getMessageType(dictionary): # Returns the type of the last message sent.
    if 'caption' in dictionary:
        return 'caption'
    elif 'photo' in dictionary:
        return 'photo'
    elif 'text' in dictionary:
        return 'text'

def sendImage(chat_id, path, caption=''): # Sends an image to the chat_id provided. Path is the location that the image is going to uploaded from. Caption is optional.
    try:
        lxybot.send_photo(chat_id=chat_id, photo=open(path, 'rb'), caption=caption)
    except FileNotFoundError:
        sendMessage('Et ole kertonut minulle {}n läksyjä!'.format(path), lastSenderId(getLastUpdate(getUpdates())))
    
def getChatTitle(update): # Gets the last message sender, or the group name, depending whether the last message was sent in a group or a private conversation.
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
        last_message = getLastUpdate(getUpdates()) # The last "message" value in the getUpdates JSON object.
        try:
            last_message_type = getMessageType(last_message['message'])
            last_message_content = last_message['message']
        except KeyError:
            try:
                last_message_type = getMessageType(last_message['edited_message'])
                last_message_content = last_message['edited_message']
            except:
                raise Exception('Not a message.')
        #print(getChatTitle())
        #print(getLastUpdate(getUpdates()))
        #print(last_message_content['text'])

        if last_message != last_message_before: # All this happens if somethig new has happened since last update.
            print('New message')
            last_title = getChatTitle(last_message)
            print(last_title)
            if last_message_type == 'text' and'@' in last_message_content['text']: # How text messages are treated.
                print(last_message_content['text'])
                chat_id = lastChatIdText(getUpdates())[1]
                kouluaine = watson(last_message_content['text'])
                print(last_title)
                path = os.environ['HOME'] + '/ibm_watson/{}/{}.jpg'.format(last_title, kouluaine)
                print(path)
                print(kouluaine)
                sendImage(chat_id, path, 'olepahyvä')
                print(watson(last_message_content['text']))
                
            elif last_message_type == 'caption' and '@' in last_message_content['caption']: # How images are treated.
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
    

    
if __name__ == '__main__': # If a foreign script calls this file, it still works.
    main()

