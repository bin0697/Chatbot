

# sessionu = {}
# if "username" in sessionu:
#     sessionu['username'] = sessionu.get('username') + 1  # reading and updating session data
# else:
#     sessionu['username'] = 1 # setting session data

# print ( "Total visits: {}".format(sessionu.get('username')) ) 



# data = {
#     "cars": {
#         "Nissan": [
#             {"model":"Sentra", "doors":4},
#             {"model":"Maxima", "doors":4},
#             {"model":"Skyline", "doors":2}
#         ],
#         "Ford": [
#             {"model":"Taurus", "doors":4},
#             {"model":"Escort", "doors":4}
#         ]
#     }
# }

# data['cars']["Nissan"].append({"model" + "tesst":"simp", "doors":12})
# print (data['cars']["Nissan"][3]  )

# test = {'state': 1}
# test.update({'cauhoi': 2})
# print (test)
# test['state'] = test['state'] - 1
# print (test)

from underthesea import word_tokenize

import sys
import numpy as np
import os
import re
from keras.models import load_model

#import sentimential as st
from keras.models import model_from_json

# Model reconstruction from JSON file
with open('/Users/mac/Desktop/PythonSocket/flask-chat-app-article-master/quessmodel_architecture-final1.json', 'r') as f:
    model = model_from_json(f.read())

# Load weights into the new model
model.load_weights('/Users/mac/Desktop/PythonSocket/flask-chat-app-article-master/quesmodel-weight-final(1).h')
wordsList = np.load('/Users/mac/Desktop/NLP/data_train/tu.npy')
print('Simplified vocabulary loaded!')
#wordsList = wordsList.tolist()
print('Size of the vocabulary: ', len(wordsList)) 
wordsList = [word.decode('UTF-8') for word in wordsList]

strip_special_chars = re.compile('[^\w0-9 ]+')

def cleanSentences(string):
    string = string.lower().replace("<br />", " ")
    return re.sub(strip_special_chars, "", string.lower())

f = ['Cho mình hỏi về vấn đề tiếng anh ở trường?']
ids = []
maxSeqLength = 180
line = f[0]
nline =  word_tokenize(cleanSentences(line), format="text")
newline = re.sub(r'_', "", nline)
split = newline.split()

for i, word in enumerate(split):
	if i >= maxSeqLength:
		break
	try:
		idx = wordsList.index(word)
		ids.append(idx)
	except ValueError:
		ids.append(518835)
        
ids = np.array(ids + ([0] * (maxSeqLength - len(ids))))
ids = np.expand_dims(ids, axis=0)
prediction = model.predict(ids)
print (ids)
print(prediction)
if prediction < 0.5: 
	print( "cmt" )
else: 
	print ( 'ques')
