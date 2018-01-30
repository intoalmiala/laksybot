import json 
import requests
import time
import wget
from watson_developer_cloud import NaturalLanguageClassifierV1, VisualRecognitionV3
import telegram
import os
import urllib

os.chdir('/home/kaappo/laksybot/ryhmät')
with open ('t.txt') as f:
    content = f.read()
ids = content.split('\n')
"""
ids = os.listdir()
"""
#ids = ['-181498996']
print(ids)

telegram_bot_token= '386957960:AAEWqf1iFMjnHk7yJfqK9pHVuWiTaxQpJ1I'

URL = "https://api.telegram.org/bot{}/".format(telegram_bot_token) # the base URL of the bot api.


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





    
def main():
    for i in ids:
        sendMessage('ÄÄlkää kuitenkaan poistako minua, koska lienen jo pian toiminnassa.', i)
                
    
if __name__ == '__main__': # If a foreign script calls this file, it still works.
    main()

