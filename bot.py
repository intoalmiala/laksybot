import json 
import requests
import time
import wget
from watson_developer_cloud import NaturalLanguageClassifierV1, VisualRecognitionV3
import telegram
import os
import urllib

try:
    os.chdir(os.environ['HOME']  + '/laksybot')   
except:
    os.mkdir(os.environ['HOME'] + '/laksybot')
    os.chdir(os.environ['HOME']  + '/laksybot')

    
# Authentication stuff
telegram_bot_token = ''
watson_v_r_token = ''
watson_nlc_password = ''
watson_nlc_username = ''

lxybot = telegram.Bot(telegram_bot_token)
URL = "https://api.telegram.org/bot{}/".format(telegram_bot_token)

def visual_recognition(path):
    def getHighestClass(response):
        response = response['images'][0]['classifiers'][0]['classes']
        classes, scores = [], []
        for i in response:
            classes.append(i['class'])
            scores.append(i['score'])
        if response[0]['score'] > response[1]['score']:
            #print(response[0]['class'])
            return response[0]['class']
        else:
            #print(response[1]['class'])
            return response[1]['class']
    visual_recognition = VisualRecognitionV3('2016-05-20', api_key=watson_v_r_token)
    response = visual_recognition.classify(images_file=open(path, 'rb'), threshold=0, classifier_ids=['liitutauluvaiei_1285787542'])
    thingy = getHighestClass(response)
    return thingy

def getTopClassConfidence(top_class, response):
    for i in response['classes']:
        if i['class_name'] == top_class:
            return i['confidence']


def watson(text): #This function deternies, which school subject is being talked about in the input string.
    natural_language_classifier = NaturalLanguageClassifierV1(
        username=watson_nlc_username,
        password=watson_nlc_password)

    response = natural_language_classifier.classify('1e0d8ex232-nlc-26798', text)
    top_class = response['top_class']
    print(getTopClassConfidence(top_class, response))
    if getTopClassConfidence(top_class, response) <= 0.45:
        return None
    else:
        return top_class


def getUrl(url): # Opens a url
    response = requests.get(url)
    content = response.content.decode("utf8")
    return content


def downloadUrl(url, name): #Downloads the contents of the input url.
    wget.download(url,out=name)


def jsonFromUrl(url): #Returns a json object from the contents of a given url.
    content = getUrl(url)
    js = json.loads(content)
    return js


update_counter = 0

def getUpdates(): # Returns a JSON object representing the events that occur during interacting with the bot.
    global update_counter
    url = URL + "getUpdates?timeout=100&alllowed_updates=['message']"
    if update_counter > 90:
        update_counter = 0
        return getUpdatesWithOffset(getLastUpdateId(getUpdatesWithOffset()))
    js = jsonFromUrl(url)
    update_counter += 1
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
        chat_id = updates["result"][last_update]["message"]["chat"]["id"]
    except:
        try:
            text = updates["result"][last_update]["edited_message"]["text"]
            chat_id = updates["result"][last_update]["edited_message"]["chat"]["id"]
        except:
            try:
                text = updates["result"][last_update]["message"]["caption"]
                chat_id = updates["result"][last_update]["message"]["chat"]["id"]
            except:
                raise Exception('Ei ole viesti')
    #chat_id = updates["result"][last_update]["message"]["chat"]["id"]
    return [text, chat_id]
    
def lastSenderId(update):
    if update['message']['chat']['type'] == 'group':
        return update['message']['chat']['id']
    if update['message']['chat']['type'] == 'private':
        return update['message']['from']['id']


def sendMessage(text, chat_id): #Sends a message to a given chat_id.
    text = urllib.parse.quote(text.encode('utf-8'))
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
        kouluaine_eroteltu = path.split('/')
        kouluaine = kouluaine_eroteltu[len(kouluaine_eroteltu) - 1]
        kouluaine = kouluaine.split('.')[0]
        sendMessage('Et ole kertonut minulle aineen {} läksyjä!'.format(kouluaine.lower()), lastSenderId(getLastUpdate(getUpdates())))
    
def getChatTitle(update): # Gets the last message sender, or the group name, depending whether the last message was sent in a group or a private conversation.
    if update['chat']['type'] == 'group':
        return update['chat']['title']
    elif update['chat']['type'] == 'private':
        return update['chat']['first_name']
    else:
        raise Exception('chatin titleä ei löytynyt')
    
    
    

def main():
    last_message_before = None
    while True:
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

        if last_message != last_message_before: # All this happens if somethig new has happened since last update.
            chat_id = lastChatIdText(getUpdates())[1]
            last_title = getChatTitle(last_message_content)
            print('Uusi viesti')
            try:
                print('Lähettäjä: {}; Viesti: {}; chat_id: {}'.format(last_title, last_message_content['caption'], chat_id))
                print(watson(last_message_content['caption']))
            except:
                try:
                    print('Lähettäjä: {}; Viesti: {}; chat_id: {}'.format(last_title, last_message_content['text'], chat_id))
                    print(watson(last_message_content['text']))
                except:
                    print('virhe')
                    pass
            
            chat_id = lastChatIdText(getUpdates())[1]
            if last_message_type == 'text' and len(last_message_content['text']) < 1024 and watson(last_message_content['text']) != None: # How text messages are treated.
                
                kouluaine = watson(last_message_content['text'])
                path = os.environ['HOME'] + '/laksybot/ryhmät/{}/'.format(last_title)
                if not os.path.isdir(path):
                    os.mkdir(path)
                path += kouluaine + '.jpg'
                sendImage(chat_id, path, 'Tässä on aineen {} läksy.'.format(kouluaine.lower()))
                
            elif last_message_type == 'caption' and len(last_message_content['caption']) < 1024 and watson(last_message_content['caption']) != None: # How images are treated.
                if len(last_message_content['caption']) > 1024:
                    continue
                caption = last_message['message']['caption']
                print('Sain kuvan, jonka käpsöni oli:', caption)
                kouluaine = watson(caption)
                if not os.path.isdir('./ryhmät/{}'.format(last_title)):
                    os.mkdir('./ryhmät/{}'.format(last_title))
                
                if not os.path.isdir('./temp/{}'.format(last_title)):
                    os.mkdir('./temp/{}'.format(last_title))
                if os.path.isfile('./temp/{}/{}.jpg'.format(last_title, kouluaine)):
                    os.remove('./temp/{}/{}.jpg'.format(last_title, kouluaine))
                getFile(getFileId(1), 'temp/{}/{}.jpg'.format(last_title, kouluaine))
                print(visual_recognition('./temp/{}/{}.jpg'.format(last_title, kouluaine)))
                if visual_recognition('./temp/{}/{}.jpg'.format(last_title, kouluaine)) == 'liitutaulu':
                    if os.path.isfile('./ryhmät/{}/{}.jpg'.format(last_title, kouluaine)):
                        os.remove('./ryhmät/{}/{}.jpg'.format(last_title, kouluaine))
                    os.rename('./temp/{}/{}.jpg'.format(last_title, kouluaine), './ryhmät/{}/{}.jpg'.format(last_title, kouluaine))
                    sendMessage('Selvä! Muistan nyt aineen {} läksyn!'.format(kouluaine.lower()), chat_id)
                else:
                    sendMessage('Hyvä yritys, mutta tuolla kuvalla ei ole mitään tekemistä läksyjen kanssa...', chat_id)
                    print('Ei ole liitutaulu.')
                print('\nKuva ladattu onnistuneesti')
                
        last_message_before = last_message
    last_message_before = last_message
    

    
if __name__ == '__main__': # If a foreign script calls this file, it still works.
    main()

