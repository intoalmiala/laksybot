{
  "url": "https://gateway-a.watsonplatform.net/visual-recognition/api",
  "note": "This is your previous free key. If you want a different one, please wait 24 hours after unbinding the key and try again.",
  "api_key": "d51997e99c32eeea53de579fa1337829f6c1c3b8"
}

import json
from os.path import join, dirname
from os import environ
from watson_developer_cloud import VisualRecognitionV3
params =  { "classifier_ids": ["liitutauluvaiei_1285787542"] }
visual_recognition = VisualRecognitionV3('2016-05-20', api_key='d51997e99c32eeea53de579fa1337829f6c1c3b8')

print(json.dumps(visual_recognition.list_classifiers(), indent=2))

with open('/home/kaaappo/Desktop/testi.jpg', 'rb') as image:
	response = visual_recognition.classify(params, images_file=image)
print(str(response))
