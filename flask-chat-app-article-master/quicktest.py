

# sessionu = {}
# if "username" in sessionu:
#     sessionu['username'] = sessionu.get('username') + 1  # reading and updating session data
# else:
#     sessionu['username'] = 1 # setting session data

# print ( "Total visits: {}".format(sessionu.get('username')) ) 



data = {
    "cars": {
        "Nissan": [
            {"model":"Sentra", "doors":4},
            {"model":"Maxima", "doors":4},
            {"model":"Skyline", "doors":2}
        ],
        "Ford": [
            {"model":"Taurus", "doors":4},
            {"model":"Escort", "doors":4}
        ]
    },
    "sth": ["hâhhaa","tesing"],
    'sth2': [1,2,3]
}
data2 = {
	'ha': "haha"
}
data2['ho'] = "hôhho"
print (data2)
# print (len(data['sth']))
# if len (data['sth']) == 1:
# 	print("ok")
# else:
# 	print("not ok")
# # kay = data.keys()
# # for key, value in data.items():
# #     print (key)
# # key, value = data.items()
# # print (key)
# # from flask import Flask, render_template, redirect, url_for, request, json
# # data['cars']["Nissan"].append({"model" + "tesst":"simp", "doors":12})
# # print (data['cars']["Nissan"][3]  )

# test = {'state': 1}
# test.update({'cauhoi': 2})
# print (test)
# test['state'] = test['state'] - 1
# print (test)

# 
# from flask import Flask, render_template, redirect, url_for, request, json
# filename = '/Users/mac/Desktop/PythonSocket/flask-chat-app-article-master/static/data/keywords.json'
# with open(filename) as test_file:
#     keywords = json.load(test_file)
# word = "tesing"
# if word in data["sth"]:
# 	print("true")
# else:
# 	print ("false")
# # for key, value in keywords["ISEaSAP"]["Học phí"][0].items():
# #     print (key)
# from underthesea import word_tokenize
# string = "Trường học là nơi dùng để ngủ"
# string = word_tokenize(string,format="text")
# print (string)
# string = string.lower().replace("_", " ")
# print(string)


