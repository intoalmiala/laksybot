{
  "url": "https://gateway-a.watsonplatform.net/visual-recognition/api",
  "note": "This is your previous free key. If you want a different one, please wait 24 hours after unbinding the key and try again.",
  "api_key": "d51997e99c32eeea53de579fa1337829f6c1c3b8"
}

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
        

import json
import os
from os.path import join, dirname
from os import environ
from watson_developer_cloud import VisualRecognitionV3
#params =  { "classifier_ids": ["liitutauluvaiei_1285787542"], 'images_file': open('/home/kaappo/Desktop/asd9.jpg', 'rb')}
visual_recognition = VisualRecognitionV3('2016-05-20', api_key='d51997e99c32eeea53de579fa1337829f6c1c3b8')

path = input()
if path == '':
    path = os.environ['HOME'] + '/Desktop/asd9.jpg'
    
response = visual_recognition.classify(images_file=open(path, 'rb'), threshold=0, classifier_ids=['liitutauluvaiei_1285787542'])
#print(response['images'][0]['classifiers'][0]['classes'])
print(getHighestClass(response))
