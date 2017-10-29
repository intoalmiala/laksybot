import json
from watson_developer_cloud import NaturalLanguageClassifierV1

natural_language_classifier = NaturalLanguageClassifierV1(
  username='5b314083-6286-4ad6-86b0-c6d0ea4aa266',
  password='mawh434bmDVG')

while(True):
	response = natural_language_classifier.classify('1e0d8ex232-nlc-26798', input())#['top_class']
	print(json.dumps(response, indent=4))