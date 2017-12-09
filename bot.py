import json 
import requests
import time
import wget
from watson_developer_cloud import NaturalLanguageClassifierV1, VisualRecognitionV3
import telegram
import os
import urllib


# Authentication stuff
telegram_bot_token= ''
watson_v_r_token = ''
watson_nlc_password = ''
watson_nlc_username = ''
watson_nlc_id = ''



lxybot = telegram.Bot(telegram_bot_token) # initializing a telegram bot instance.
URL = "https://api.telegram.org/bot{}/".format(telegram_bot_token) # the base URL of the bot api.

# Creating some directories if they do not exist.
try:
    os.chdir(os.environ['HOME']  + '/laksybot')   
except:
    os.mkdir(os.environ['HOME'] + '/laksybot')
    os.chdir(os.environ['HOME']  + '/laksybot')
if not os.path.isdir(os.environ['HOME']  + '/laksybot/temp'): # ./temp is used to store the images, until they are classified by the visual recognition service...
    os.mkdir(os.environ['HOME']  + '/laksybot/temp')
if not os.path.isdir(os.environ['HOME']  + '/laksybot/ryhmät'): # ... after that, they are moved into ./ryhmät dir.
    os.mkdir(os.environ['HOME']  + '/laksybot/ryhmät')


def visual_recognition(path):
    """
    Desc: 
        Returns, whether or not a given input is a picture about a black board.
    Takes:
        str path    : A string containing the path to the image that is going to be classified.
    Returns:
        str thingy  : whether a string containing 'liitutaulu' or 'epäliitutaulu', depending the outcome of the Visual Recognition service.
    Note:
        None
    Raises:
        None
    """
    def getHighestClass(response):
        """
        Desc: 
            Returns the class with highest score from the JSON object that the parent funtion returns.
        Takes:
            JSON response   : the JSON object that the parent function returns.
        Returns:
            float   : The highest score out of the classes.
        Note:
            Works only with the parent function; nothing else.
        Raises:
            None.
        """
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

def watson(text): #This function determines, which school subject is being talked about in the input string.
    """
    Desc:
        An IBM Watson Natural Language Classifier instance, that determines, what school subjet is being talked about.
    Takes:
        str text        : The input string that the function classifies.
    Returns:
        str top_class   : The school subject with the highest confidence. 
        IF the confidence is under the certain point, it returns only
        none None
    Notes:
        None
    Raises:
        None
    """
    def getTopClassConfidence(top_class, response):
        """
        Desc:
            Returns the confidence of the parent funtion's top_class str.
        Takes:
            str top_class   : The class with the highes confidence; See the desc of the parent function.
            JSON response   : The JSON object representing the response from the IBM NLC.
        Retunrs:
            float confidence    : The confidence of the top class.
        Note:
            Only works together with the parent funcntion.
        Raises:
            None
        """
        for i in response['classes']:
            if i['class_name'] == top_class:
                return i['confidence']

    natural_language_classifier = NaturalLanguageClassifierV1(
        username=watson_nlc_username,
        password=watson_nlc_password)

    response = natural_language_classifier.classify(watson_nlc_id, text)
    top_class = response['top_class']
    print(getTopClassConfidence(top_class, response))
    if top_class == 'keskustelu':
        return None
    else:
        return top_class

def getUrl(url):
    """
    Desc:
        Returns the content of a given URL.
    Takes:
        str url : A URL of which's content is going to be returned.
    Returns:
        str content : The contents of the URL
    Note:
        None
    Raises:
        None
    """
    response = requests.get(url)
    content = response.content.decode("utf8")
    return content

def downloadUrl(url, name):
    """
    Desc:
        Downloads the contents of the input URL.
    Takes:
        str url     : The URL to download
        str name    : The name for the downloaded content
    Returns:
        None
    Note:
        None
    Raises:
        None
    """
    wget.download(url,out=name)

def jsonFromUrl(url):
    """
    Desc:
        Returns a JSON object from the contents of a given URL.
    Takes:
        str url : The url where the JSON is
    Returns:
        dict js : The JSON from the URL as a dictionary
    Note:
        None
    Raises:
        None
    """
    content = getUrl(url)
    js = json.loads(str(content))
    return js


def getUpdates(offset=None): 
    url = URL + 'getUpdates'
    if offset:
        url += '?offset={}'.format(offset)
    return jsonFromUrl(url)

def lastChatIdText(updates): 
    """
    Desc:
        Gives the chat id of the last message sent.
    Takes:
        JSON updates : A JSON object of the same form as that is returned from the getUpdates() function.
    Returns:
        list conatining the last message text and the chat id of the last message sender.
    Note:
        Somewhat unstable fucntion at the moment.
    Raises:
        Exception('Ei ole viesti') when it cannot find any text from the last message sent.
    """
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
    return [text, chat_id]
    
def lastSenderId(update):
    """
    Desc:
        If the last message was sent via a group, the group id is returned instead.
    Takes:
        JSON update : A JSON object of the same form as that is returned from the getUpdates() function.
    Returns:
        str contaning the id of the sender or a group.
    Note:
        Possibly going to be removed a some point.
    Raises:
        None
     """
    if update['message']['chat']['type'] == 'group':
        return update['message']['chat']['id']
    if update['message']['chat']['type'] == 'private':
        return update['message']['from']['id']

def sendMessage(text, chat_id): 
    """
    Desc:
        Sends a message with a given text to a given content.
    Takes:
        str text : The message that is going to be sent.
        str chat_id : the chat id that the message is being sent to.
    Returns:
        None
    Note:
        None
    Raises:
        None
    """
    text = urllib.parse.quote(text.encode('utf-8'))
    url = URL + "sendMessage?text={}&chat_id={}".format(text, chat_id)
    print('Lähetin viestin: {} {}:lle'.format(text, chat_id))
    getUrl(url)

def getLastUpdateId(updates):
    """
    Desc:
        Returns the last update id.
    Takes:
        JSON updates : A JSON object of the same form as that is returned from the getUpdates() function.
    Returns:
        int update_id : The update id of the last update.
    Note:
        None
    Raises:
        None
    """
    
    update_ids = []
    for update in updates["result"]:
        update_ids.append(int(update["update_id"]))
    return max(update_ids)

def getLastUpdate(updates):
    for i in updates['result']:
        if i['update_id'] == getLastUpdateId(updates):
            return i

def getFile(file_id, path):
    """
    Desc:
        Downloads an image from telegram servers.
    Takes:
        int file_id : Specifies which image is the one to be downloaded.
        str path : The local file path that the image is going to be saved to.
    Returns:
        None
    Note:
        None
    Raises:
        None
    """
    json = jsonFromUrl(URL + 'getFile?file_id={}'.format(file_id))
    url = 'https://api.telegram.org/file/bot{}/{}'.format(telegram_bot_token, json['result']['file_path'])
    downloadUrl(url, path)

def getFileId(resolution): 
    """
    Desc:
        Gets the best-quality id to the last image sent.
    Takes:
        bool resolution : if True, returns the best-quality id, if False, returns the worst-quality id.
    Returns:
        str i['file_id'] : the file id that sepcifies the file that is downloaded by the getFile() function.
    Note:
        None
    Raises:
        None
    """
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
    """
    Desc:
        gets the type of the last message sent.
    Takes:
        dict dictionary : dictionary representing the last message.
    Returns:
        str : 'text' if the last message type is text, 'photo' if photo and 'caption' if an image with a caption
    Note:
        None
    Raises:
        None
    """
    if 'caption' in dictionary and 'photo' in dictionary:
        return 'caption'
    elif 'photo' in dictionary:
        return 'photo'
    elif 'text' in dictionary:
        return 'text'

def sendImage(chat_id, path, updates, caption=''): 
    """
    Desc:
        Sends an image to a user.
    Takes:
        str chat_id : The chat id that the message sent to.
        str path : The local path containing the image to be sent.
        str caption : (optional) Caption sent along the image
     Returns:
        None
    Note:
        If path not found, sends a message to the user saying that they haven't told the homework .
    Raises:
        None
    """
    try:
        lxybot.send_photo(chat_id=chat_id, photo=open(path, 'rb'), caption=caption)
    except FileNotFoundError:
        kouluaine_eroteltu = path.split('/')
        kouluaine = kouluaine_eroteltu[len(kouluaine_eroteltu) - 1]
        kouluaine = kouluaine.split('.')[0]
        sendMessage('Et ole kertonut minulle aineen {} läksyjä!'.format(kouluaine.lower()), lastSenderId(getLastUpdate(updates)))
    
def getChatTitle(update): 
    """
    Desc:
        returns the chat title pf the last message sent.
    Takes:
        JSON update : A JSON object of the same form as that is returned from the getUpdates() function.
    Returns:
        str : chat title of the conversation that the last message was sent from.
    Note:
        None
    Raises:
        Exception('chatin titleä ei löytynyt') : If no chat title is not found.
    """
    if update['chat']['type'] == 'group':
        return update['chat']['title']
    elif update['chat']['type'] == 'private':
        return update['chat']['first_name']
    else:
        raise Exception('chatin titleä ei löytynyt')

def getMessageStuff(last_message):
    try:
        last_message_type = getMessageType(last_message['message'])
        last_message_content = last_message['message']
    except KeyError:
        try:
            last_message_type = getMessageType(last_message['edited_message'])
            last_message_content = last_message['edited_message']
        except:
            raise Exception('Not a message.')
    return (last_message_type, last_message_content)



    
def main():
    last_update_id = None
    while True: # The super-duper-hyper-ultra-extra master champion aka main loop
        updates = getUpdates(last_update_id)
        if len(updates['result']) > 0:
            last_message = getLastUpdate(updates) # The last "message" value in the getUpdates JSON object.
            last_message_type, last_message_content = getMessageStuff(last_message)
            last_update_id = getLastUpdateId(updates) + 1
            if last_message_type != 'photo':
                try:
                    chat_id = lastChatIdText(updates)[1]
                except Exception:
                    continue
            else:
                continue
            last_title = getChatTitle(last_message_content)
            print('Uusi viesti')
            if last_message_type == 'text':
                parsed_text = watson(last_message_content['text'])
            elif last_message_type == 'caption':
                parsed_text = watson(last_message_content['caption'])
            try:
                print('Lähettäjä: {}; chat_id: {}'.format(last_title, chat_id))
                print(parsed_text)
            except:
                try:
                    print('Lähettäjä: {}; chat_id: {}'.format(last_title, chat_id))
                    print(parsed_text)
                except:
                    print('virhe')
                    pass
            
            chat_id = lastChatIdText(updates)[1]
            if last_message_type == 'text' and len(last_message_content['text']) < 1024 and parsed_text != None: # How text messages are treated.
                 
                path = os.environ['HOME'] + '/laksybot/ryhmät/{}/'.format(chat_id)
                
                if not os.path.isdir(path):
                    os.mkdir(path)
                path += parsed_text + '.jpg'
                print(path)
                sendImage(chat_id, path, updates, 'Tässä on aineen {} läksy.'.format(parsed_text.lower()))
                
            elif last_message_type == 'caption' and len(last_message_content['caption']) < 1024 and parsed_text != None: # How images are treated.
                if len(last_message_content['caption']) >= 1024:
                    continue
                caption = last_message['message']['caption']
                print('Sain kuvan, jonka käpsöni oli:', caption)
                if not os.path.isdir('./ryhmät/{}'.format(chat_id)):
                    os.mkdir('./ryhmät/{}'.format(chat_id))
                if not os.path.isdir('./temp/{}'.format(chat_id)):
                    os.mkdir('./temp/{}'.format(chat_id))
                if os.path.isfile('./temp/{}/{}.jpg'.format(chat_id, parsed_text)):
                    os.remove('./temp/{}/{}.jpg'.format(chat_id, parsed_text))
                getFile(getFileId(1), 'temp/{}/{}.jpg'.format(chat_id, parsed_text))
                print(visual_recognition('./temp/{}/{}.jpg'.format(chat_id, parsed_text)))
                if visual_recognition('./temp/{}/{}.jpg'.format(chat_id, parsed_text)) == 'liitutaulu':
                    if os.path.isfile('./ryhmät/{}/{}.jpg'.format(chat_id, parsed_text)):
                        os.remove('./ryhmät/{}/{}.jpg'.format(chat_id, parsed_text))
                    os.rename('./temp/{}/{}.jpg'.format(chat_id, parsed_text), './ryhmät/{}/{}.jpg'.format(chat_id, parsed_text))
                    sendMessage('Selvä! Muistan nyt aineen {} läksyn!'.format(parsed_text.lower()), chat_id)
                else:
                    sendMessage('Hyvä yritys, mutta tuolla kuvalla ei ole mitään tekemistä läksyjen kanssa...', chat_id)
                    print('Ei ole liitutaulu.')
                print('\nKuva ladattu onnistuneesti')
                
    
if __name__ == '__main__': # If a foreign script calls this file, it still works.
    main()

