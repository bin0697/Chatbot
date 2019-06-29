from flask import Flask, render_template, redirect, url_for, request, json
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from flask_restful import Resource, Api
from flask_bootstrap import Bootstrap
import pandas as pd
import difflib
from fuzzywuzzy import fuzz
import xlrd 
from flask_wtf import FlaskForm 
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import InputRequired, Email, Length
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
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

with open('/Users/mac/Desktop/PythonSocket/flask-chat-app-article-master/posmodel_architecture7-6.json', 'r') as fa:
    model2 = model_from_json(fa.read())
model2.load_weights('/Users/mac/Desktop/PythonSocket/flask-chat-app-article-master/posmodel-weight7-6.h')

# with open('/Users/mac/Desktop/PythonSocket/flask-chat-app-article-master/posmodel_architecture100epoch.json', 'r') as fa:
#     model2 = model_from_json(fa.read())
# model2.load_weights('/Users/mac/Desktop/PythonSocket/flask-chat-app-article-master/posmodel-weight(100epoch).h')

wordsList = np.load('/Users/mac/Desktop/NLP/data_train/tu.npy')

wordsListpos = np.load('/Users/mac/Desktop/NLP/data_train/wordsList.npy')
wordsListpos = wordsListpos.tolist()

print('Simplified vocabulary loaded!')
#wordsList = wordsList.tolist()
print('Size of the vocabulary: ', len(wordsList)) 
wordsList = [word.decode('UTF-8') for word in wordsList]

strip_special_chars = re.compile('[^\w0-9 ]+')

def cleanSentences(string):
    string = string.lower().replace("<br />", " ")
    return re.sub(strip_special_chars, "", string.lower())
def predictquescmt(mess):
	#f = ['Mình chỉ muốn góp ý là nhà vệ sinh cần phải đc dọn sạch sẽ hơn']
	ids = []
	maxSeqLength = 180
	#line = f[0]
	line = mess
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
	    return "cmt"
	else: 
	    return 'ques'

def predictposneg(mess):
	#f = ['Mình chỉ muốn góp ý là nhà vệ sinh cần phải đc dọn sạch sẽ hơn']
	ids = []
	maxSeqLength = 180
	#line = f[0]
	line = mess
	nline =  word_tokenize(cleanSentences(line), format="text")
	split = nline.split()

	for i, word in enumerate(split):
	    if i >= maxSeqLength:
	        break
	    try:
	        idx = wordsListpos.index(word)
	        #idx = wordsList.index(word)
        	ids.append(idx)
	    except ValueError:
	        ids.append(wordsListpos.index('UNK'))
	        #ids.append(wordsList.index('UNK'))
	        
	ids = np.array(ids + ([0] * (maxSeqLength - len(ids))))
	ids = np.expand_dims(ids, axis=0)
	prediction = model2.predict(ids)
	print (ids)
	print(prediction)
	if prediction > 0.5: 
	    return "pos"
	else: 
	    return "neg"
#import json
# from models import Product, Purchase, User, db
# from forms import FreeBookForm, LoginForm

# rom flask.ext.login import LoginManager, login_required, login_user, logout_user, current_user
# #logger = logging.getLogger(__name__)
# #bull = Blueprint('bull', __name__)
# login_manager = LoginManager()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'vnkdjnfjknfl1232#'
Bootstrap(app)
socketio = SocketIO(app)
# db_connect = create_engine('sqlite:////Users/mac/Desktop/PythonSocket/flask-chat-app-article-master/databse')
# api = Api(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////Users/mac/Desktop/PythonSocket/flask-chat-app-article-master/databse'
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

guive = {}
rulekeywords = {}
import xlrd
book = xlrd.open_workbook('/Users/mac/Desktop/FQA.xlsx')
dhqt = book.sheet_by_name('P.QHĐN')
ctlk = book.sheet_by_name('CTLK')
data = [dhqt.cell_value(r, c) for c in range(2) for r in range(1,dhqt.nrows)]
answer = [dhqt.cell_value(r, 1) for r in range(1,dhqt.nrows)]
data2 = [ctlk.cell_value(r, c) for c in range(2) for r in range(1,ctlk.nrows)]
answer2 = [ctlk.cell_value(r, 1) for r in range(1,ctlk.nrows)]
#filename = os.path.join(app.static_folder, 'data', 'keywords.json')
filename = '/Users/mac/Desktop/PythonSocket/flask-chat-app-article-master/static/data/keywords.json'
with open(filename) as test_file:
    keywords = json.load(test_file)
print (keywords)

keyDHQT = ["học phí", "tuyển sinh", "ngôn ngữ", "trình độ"]
keyDongy =['yup', 'đúng', 'đúng rồi','yes','ok', 'okay', 'ừ']
keyKodongy = ['ko', 'không', 'không đúng', 'no', 'không phải', 'nope']

#     def is_anonymous(self):
#         """False, as anonymous users aren't supported."""
#         return False

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column('user_name',db.String(15), unique=True)
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(80))


class Messages(db.Model):
	__tablename__ = 'Messages'
	id = db.Column('id', db.Integer, primary_key=True)
	message = db.Column('message', db.String(500))
	name = db.Column('user_name', db.String(500))

class Positive(db.Model):
	__tablename__ = 'Positive'
	id = db.Column('id', db.Integer, primary_key=True)
	comment = db.Column('comment', db.String(500))

class Negative(db.Model):
	__tablename__ = 'Negative'
	id = db.Column('id', db.Integer, primary_key=True)
	comment = db.Column('comment', db.String(500))

class UnanswerQuestion(db.Model):
	__tablename__ = 'UnanswerQuestion'
	id = db.Column('id', db.Integer, primary_key=True)
	sheet = db.Column('sheet', db.String(500))
	question = db.Column('question', db.String(500))
# class User(db.Model):
# 	__tablename__ = 'User'
# 	id = db.Column('id', db.Integer, primary_key=True)
# 	password = db.Column('password', db.String(500))
# 	username = db.Column('user_name', db.String(500))


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class LoginForm(FlaskForm):
    username = StringField('user_name', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=80)])
    remember = BooleanField('remember me')

class RegisterForm(FlaskForm):
    email = StringField('email', validators=[InputRequired(), Email(message='Invalid email'), Length(max=50)])
    username = StringField('user_name', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=80)])


def preintend(mess, username): 
	intend = ['hi', 'hello', 'xin chao']
	needle = mess
	maxi = 0 
	result = 'ask'
	for hay in intend:
	    ratio = fuzz.token_set_ratio(needle, hay)
	    print('%.5f' % ratio + " " + hay)
	    if ratio >= 70:
	    	maxi = ratio
	    	result = 'gthieu'
	    elif result == 'ask':
	    	result = predictquescmt(mess)
	return result


def predictdhqt(json, maxi,maxi1,maxi2):
	count = 0 
	needle = json['message']
	maxi = maxi  
	maxi1 = maxi1
	maxi2 = maxi2
	for hay in data:
	    ratio = fuzz.token_set_ratio(needle, hay)
	    print('%.5f' % ratio + " " + hay)
	    if ratio >= maxi:
	    	if count < 3:
	    		guive[json['user_name']]['cau'+ str(count)] = {'from': 'dhqt', 'index': data.index(hay)}
	    		count += 1
	    	else:
	    		guive[json['user_name']]['cau0'] = guive[json['user_name']]['cau1'] 
	    		guive[json['user_name']]['cau1'] = guive[json['user_name']]['cau2']
	    		guive[json['user_name']]['cau2'] = {'from': 'dhqt', 'index': data.index(hay)}
	    	maxi = ratio
	    elif (ratio >= maxi1 and ratio < maxi):
	    	if count == 1:
	    		guive[json['user_name']]['cau1'] = guive[json['user_name']]['cau0'] 
	    		guive[json['user_name']]['cau0'] = {'from': 'dhqt', 'index': data.index(hay)}
	    		#result = data.index(hay) 
	    		count += 1
	    	else:
	    		guive[json['user_name']]['cau0'] = guive[json['user_name']]['cau1'] 
	    		guive[json['user_name']]['cau1'] = {'from': 'dhqt', 'index': data.index(hay)}
	    		#result = data.index(hay)
	    	maxi1 = ratio

	    elif (ratio >= maxi2 and ratio < maxi1) :
	    	if count == 2:
	    		guive[json['user_name']]['cau2'] = guive[json['user_name']]['cau1']
	    		guive[json['user_name']]['cau1'] = guive[json['user_name']]['cau0']  
	    		guive[json['user_name']]['cau0'] = {'from': 'dhqt', 'index': data.index(hay)}
	    		maxi2 = ratio
	    		#result = data.index(hay) 
	    		count += 1
	    	else:
	    		guive[json['user_name']]['cau0'] = {'from': 'dhqt', 'index': data.index(hay)}
	    	maxi2 = ratio
	    		#result = data.index(hay) 
	    #print(guive[json['user_name']]['cau2'])
	return maxi,maxi1,maxi2

def predictCtlk(json, maxi,maxi1,maxi2):
	needle = json['message']
	maxi = maxi  
	maxi1 = maxi1
	maxi2 = maxi2
	for hay in data2:
	    ratio = fuzz.token_set_ratio(needle, hay)
	    print('%.5f' % ratio + " " + hay)
	    if ratio >= maxi:
    		guive[json['user_name']]['cau0'] = guive[json['user_name']]['cau1'] 
    		guive[json['user_name']]['cau1'] = guive[json['user_name']]['cau2']
    		guive[json['user_name']]['cau2'] = {'from': 'ctlk', 'index': data2.index(hay)}
    		result = data2.index(hay) 
    		maxi = ratio

	    elif (ratio >= maxi1 and ratio < maxi):
    		guive[json['user_name']]['cau0'] = guive[json['user_name']]['cau1'] 
    		guive[json['user_name']]['cau1'] = {'from': 'ctlk', 'index': data2.index(hay)}
    		maxi1 = ratio
	    		#result = data.index(hay)

	    elif (ratio >= maxi2 and ratio < maxi1) :
    		guive[json['user_name']]['cau0'] = {'from': 'ctlk', 'index': data2.index(hay)}
    		maxi2 = ratio
    		#result = data.index(hay) 
		    		


def predict(json):
	maxi = 0 
	maxi1 = 0
	maxi2 = 0
	if guive[json['user_name']]['state'] == 2:
		if rulekeywords[json['user_name']]['sheet'] == "đhqt":
			print ("tu cho predict state 2")
			predictdhqt(json, maxi,maxi1,maxi2)
		elif rulekeywords[json['user_name']]['sheet'] == "ctlk":
			predictCtlk(json, maxi,maxi1,maxi2)
		guive[json['user_name']]['state'] = 3


	else:
		maxi,maxi1,maxi2 = predictdhqt(json, maxi,maxi1,maxi2)
		predictCtlk(json, maxi,maxi1,maxi2)

		
	print(guive[json['user_name']]['cau2']) 
	nguon = guive[json['user_name']]['cau2']['from']
	print ("tu cho in predict: "+ nguon)
	index = guive[json['user_name']]['cau2']['index']
	#print (index)
	if nguon == 'dhqt':
		if index >= dhqt.nrows-1:
			index = index - dhqt.nrows + 1 
		return data[index]
	elif nguon == 'ctlk':
		if index >= ctlk.nrows-1:
			index = index - ctlk.nrows + 1 
		return data2[index]		
	#sessionu = {username : data[index]}


def handle3cauhoi(json):
	for word in word_tokenize(json['message']):
		if word in keyKodongy:
		#if json['message'] == 'ko':
			if guive[json['user_name']]['cautrl'] != -1 :

				nguon = guive[json['user_name']]['cau' + str(guive[json['user_name']]['cautrl'])]['from']
				print (nguon)
				index = guive[json['user_name']]['cau' + str(guive[json['user_name']]['cautrl'])]['index']
				guive[json['user_name']]['cautrl'] = guive[json['user_name']]['cautrl'] - 1
				#print (index)
				sendback = ''
				if nguon == 'dhqt':
					if index >= dhqt.nrows-1:
						index = index - dhqt.nrows + 1 
					#sendback = data[index]
					pre = 'Có phải bạn muốn hỏi: ' + data[index]
				elif nguon == 'ctlk':
					if index >= ctlk.nrows-1:
						index = index - ctlk.nrows + 1
					#sendback = data2[index]
					pre = 'Có phải bạn muốn hỏi: ' + data2[index]	
				#sessionu = {username : data[index]}
				#pre = 'Có phải bạn muốn hỏi: ' + sendback
				serpre = Messages(message=pre,name="server" + json['user_name'])
				#guive[json['user_name']]['cautrl'] = guive[json['user_name']]['cautrl'] - 1
			elif guive[json['user_name']]['cautrl'] == -1:
				if guive[json['user_name']]['state'] == 3:
					pre, serpre = resetses(json)
				else:
					guive[json['user_name']]['state'] = 2
					pre, serpre = initrulebase(json)
			break

			# pre = 'Có vẻ như mình không đoán được câu hỏi rồi, bạn vui lòng trả lời mình vài câu để đoán đúng hơn nha :)\n Bạn muốn hỏi về ĐHQT hay là ISEaSAP (chương trình trao đổi)?'
			# serpre = Messages(message=pre,name="server" + json['user_name'])
		if word in keyDongy:
		#if json['message'] == 'yup':
			#guive[json['user_name']]['cautrl'] = guive[json['user_name']]['cautrl'] - 1 
			nguon = guive[json['user_name']]['cau' + str(guive[json['user_name']]['cautrl']+1)]['from']
			index = guive[json['user_name']]['cau' + str(guive[json['user_name']]['cautrl']+1)]['index']
			#print (index)
			if nguon == 'dhqt':
				if index >= dhqt.nrows-1:
					index = index - dhqt.nrows + 1 
				#sendback = data[index]
				pre = answer[index]
			elif nguon == 'ctlk':
				if index >= ctlk.nrows-1:
					index = index - ctlk.nrows + 1
				#sendback = data2[index] 
				pre = answer2[index]
			serpre = Messages(message=pre,name="server" + json['user_name'] )
			guive[json['user_name']] = {'state' :0}
			break
	return pre, serpre 

def get3answer(json):
	guive[json['user_name']] = {'cautrl' : 1, 'state' : 1, 'oriques':json['message'] } # setting session data
	pre = 'Có phải bạn muốn hỏi: ' + predict(json)
	serpre = Messages(message=pre,name="server" + json['user_name'])
	return pre, serpre 

def get3answerfromtree(json):
	guive[json['user_name']]['cautrl'] = 1
	pre = 'Có phải bạn muốn hỏi: ' + predict(json)
	serpre = Messages(message=pre,name="server" + json['user_name'])
	return pre, serpre 




#RULED-BASE BOT

def guessQues(json):
	mess = ''
	for i in rulekeywords[json['user_name']]['keyarray']:
		mess = mess + i
	ujson = {'user_name': json['user_name'], 'message': mess}
	pre, serpre = get3answerfromtree(ujson)
	del ujson
	guive[json['user_name']]['sheet'] = rulekeywords[json['user_name']]['sheet']
	del rulekeywords[json['user_name']]
	return pre, serpre


def initrulebase(json):
	rulekeywords[json['user_name']] = {'state': 0, 'keyarray': []}
	oriques = guive[json['user_name']]['oriques'].lower()
	oriques = word_tokenize(oriques)
	print (oriques)
	pre = 'Có vẻ như mình không đoán được câu hỏi rồi, bạn vui lòng trả lời mình vài câu để đoán đúng hơn nha :) <br> Bạn muốn hỏi về ĐHQT hay là ISEaSAP (chương trình trao đổi)?'
	serpre = Messages(message=pre,name="server" + json['user_name'])
	#oriques = word_tokenize('fuck you bith')
	for word in oriques:
		if word in keywords:
			rulekeywords[json['user_name']]['keyarray'].append(word)
			if word == 'đhqt':
				rulekeywords[json['user_name']]['sheet'] = "đhqt"
				rulekeywords[json['user_name']]['state'] = 0.1
				for word in oriques:
					if word in keywords["đhqt"]:
						rulekeywords[json['user_name']]['keyarray'].append(word)
						rulekeywords[json['user_name']]['state'] = 1.1
						nextkey = word
						if len(keywords["đhqt"][nextkey]) != 1:
							for word in oriques:
								if word in keywords["đhqt"][nextkey]:
									rulekeywords[json['user_name']]['keyarray'].append(word)
									rulekeywords[json['user_name']]['state'] = 2.1
									break
						break
				pre, serpre = handletree(json)
			elif word == 'iseasap':
				rulekeywords[json['user_name']]['sheet'] = "ctlk"
				rulekeywords[json['user_name']]['state'] = 1.2
				for word in oriques:
					if word in keywords["iseasap"]:
						rulekeywords[json['user_name']]['keyarray'].append(word)
						rulekeywords[json['user_name']]['state'] = 1.2
						rulekeywords[json['user_name']]['nextword'] = word
						nextkey = word
						if len(keywords["iseasap"][nextkey]) != 1:
							for word in oriques:
								if word in keywords["iseasap"][nextkey]:
									rulekeywords[json['user_name']]['keyarray'].append(word)
									rulekeywords[json['user_name']]['state'] = 2.2
									break
						break
				pre, serpre = handletree(json)
			break
	return pre, serpre 


def handletree(json):
	oriques = guive[json['user_name']]['oriques'].lower()
	oriques = word_tokenize(oriques)
	json['message'] = json['message'].lower()
	if rulekeywords[json['user_name']]['state'] == 0:
		rulekeywords[json['user_name']]['keyarray'].append(json['message'])
		if json['message'] == 'đhqt':
			rulekeywords[json['user_name']]['sheet'] = "đhqt"
			rulekeywords[json['user_name']]['state'] = 0.1
			for word in oriques:
				if word in keywords["đhqt"]:
					json['message'] = word
					rulekeywords[json['user_name']]['state'] = 1.1
					rulekeywords[json['user_name']]['laststate'] = 0
					nextkey = word
					break

		elif json['message'] == 'iseasap':
			rulekeywords[json['user_name']]['sheet'] = "ctlk"
			rulekeywords[json['user_name']]['state'] = 0.2
			for word in oriques:
				if word in keywords["iseasap"]:
					json['message'] = word
					rulekeywords[json['user_name']]['state'] = 1.2
					rulekeywords[json['user_name']]['laststate'] = 0
					nextkey = word
					break

#--------------BEGIN OF SECOND LAYER----------

	if rulekeywords[json['user_name']]['state'] == 0.1:
		rulekeywords[json['user_name']]['state'] = 1.1
		sendbackmess = 'Bạn muốn biết mục nào của ĐHQT?'
		for key, value in keywords["đhqt"].items():
			sendbackmess = sendbackmess + "<br>-" + key
		pre = sendbackmess
		serpre = Messages(message=pre,name="server" + json['user_name'])

	if rulekeywords[json['user_name']]['state'] == 0.2:
		rulekeywords[json['user_name']]['state'] = 1.2
		rulekeywords[json['user_name']]['laststate'] = 0.2
		sendbackmess = 'Bạn muốn biết mục nào của chương trình trao đổi?'
		for key, value in keywords["iseasap"].items():
			sendbackmess = sendbackmess + "<br>-" + key
		pre = sendbackmess
		serpre = Messages(message=pre,name="server" + json['user_name'])

#--------------BEGIN OF THIRD LAYER----------

#--------------FOR ĐHQT----------

	elif rulekeywords[json['user_name']]['state'] == 1.1:
		rulekeywords[json['user_name']]['keyarray'].append(json['message'])
		nextkey = json['message']
		rulekeywords[json['user_name']]['state'] = 2.1

		if len(keywords["đhqt"][nextkey]) != 1:
			for word in oriques:
				if word in keywords["đhqt"][nextkey]:
					rulekeywords[json['user_name']]['keyarray'].append(word)
					rulekeywords[json['user_name']]['state'] = 3.1
					break
		if len(keywords["đhqt"][nextkey]) != 1 and rulekeywords[json['user_name']]['state'] != 3.1:
			sendbackmess = 'Bạn muốn biết về mục nào?'
			for mess in keywords["đhqt"][nextkey]:
				sendbackmess = sendbackmess + "<br>-" + mess
			pre = sendbackmess
			serpre = Messages(message=pre,name="server" + json['user_name'])

		else:
			pre, serpre = guessQues(json)

	elif rulekeywords[json['user_name']]['state'] == 3.1:
		rulekeywords[json['user_name']]['keyarray'].append(json['message'])
		nextkey = json['message']
		pre, serpre = guessQues(json)


#--------------FOR CTLK----------

	elif rulekeywords[json['user_name']]['state'] == 1.2:
		rulekeywords[json['user_name']]['keyarray'].append(json['message'])
		rulekeywords[json['user_name']]['nextkey'] = json['message']
		nextkey = json['message']
		rulekeywords[json['user_name']]['state'] = 2.2

		sendbackmess = 'Bạn muốn biết về mục nào của ' + nextkey +'?'
		for mess in keywords["iseasap"][nextkey]:
			sendbackmess = sendbackmess + "<br>-" + mess
		pre = sendbackmess
		serpre = Messages(message=pre,name="server" + json['user_name'])

		for word in oriques:
			if word in keywords["iseasap"][nextkey]:
				rulekeywords[json['user_name']]['keyarray'].append(word)
				pre, serpre = guessQues(json)
				break

	elif rulekeywords[json['user_name']]['state'] == 2.2:
		rulekeywords[json['user_name']]['keyarray'].append(json['message'])
		pre, serpre = guessQues(json)
		

	return pre, serpre





# @login_manager.user_loader
# def user_loader(user_id):
#     """Given *user_id*, return the associated User object.

#     :param unicode user_id: user_id (email) user to retrieve

#     """
#     return User.query.get(user_id)

# @app.route("/login", methods=["GET", "POST"])
# def login():
#     """For GET requests, display the login form. 
#     For POSTS, login the current user by processing the form.

#     """
#     print (db)
#     form = LoginForm()
#     if form.validate_on_submit():
#         user = User.query.get(form.email.data)
#         if user:
#             if bcrypt.check_password_hash(user.password, form.password.data):
#                 user.authenticated = True
#                 db.session.add(user)
#                 db.session.commit()
#                 login_user(user, remember=True)
#                 return redirect(url_for("app.chat"))
#     return render_template("login.html", form=form)

# @app.route("/logout", methods=["GET"])
# @login_required
# def logout():
#     """Logout the current user."""
#     user = current_user
#     user.authenticated = False
#     db.session.add(user)
#     db.session.commit()
#     logout_user()
#     return render_template("logout.html")

# Route for handling the login page logic
# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     error = None
#     if request.method == 'POST':
#         if request.form['username'] != 'admin' or request.form['password'] != 'admin':
#             error = 'Invalid Credentials. Please try again.'
#         else:
#             return redirect(url_for('home'))
#     return render_template('login.html', error=error)

def resetses(json):
	pre = 'Có vẻ như câu hỏi của bạn không có trong hệ thống của mình rồi. Mình sẽ lâu câu hỏi của bạn vào database để trường biết nha :)'
	serpre = Messages(message=pre,name="server" + json['user_name'])
	db.session.add(UnanswerQuestion(sheet = guive[json['user_name']]['sheet'],question=guive[json['user_name']]['oriques'].lower()))
	guive[json['user_name']] = {'state' :0}
	return pre, serpre 


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if check_password_hash(user.password, form.password.data):
                login_user(user, remember=form.remember.data)
                #sessionu[user.username] = user.username
                guive[form.username.data] = {'state' :0}
                return redirect('/chat/' + form.username.data)

        return '<h1>Invalid username or password</h1>'
        #return '<h1>' + form.username.data + ' ' + form.password.data + '</h1>'

    return render_template('login.html', form=form)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = RegisterForm()

    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data, method='sha256')
        new_user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        return '<h1>New user has been created!</h1>'
        #return '<h1>' + form.username.data + ' ' + form.email.data + ' ' + form.password.data + '</h1>'

    return render_template('signup.html', form=form)

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', name=current_user.username)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/chat/<username>')
@login_required
def chat(username):
	messages = Messages.query.filter((Messages.name == username)|( Messages.name == 'server'+username ))
	#guive[username] = {'state' :0}
	return render_template('chat_detail.html', name=current_user.username, messages = messages)

def messageReceived(methods=['GET', 'POST']):
    print('message was received!!!')


@socketio.on('my event')
def handle_my_custom_event(json, methods=['GET', 'POST']):
	print('received my event: ' + str(json))
	message = Messages(message=json['message'],name=json['user_name'])
	db.session.add(message)
	if guive[json['user_name']]['state'] == 0:
		if preintend(json['message'], json['user_name']) == 'gthieu':
			pre = 'Chào bạn, bạn có thể hỏi hoặc cmt góp ý với mình :)'
			serpre = Messages(message=pre,name="server" + json['user_name'])
		elif preintend(json['message'], json['user_name']) == 'cmt':

			if predictposneg(json['message']) == 'pos':
				db.session.add(Positive(comment=json['message']))
				pre = 'Cảm ơn bạn đã góp ý, mình sẽ lưu vào hệ thống để báo cho trường :)'
				serpre = Messages(message=pre,name="server" + json['user_name'])

			elif predictposneg(json['message']) == 'neg':
				db.session.add(Negative(comment=json['message']))
				pre = 'Mình xin lỗi bạn về điều đó, mình sẽ lưu vào hệ thống để báo cho trường :('
				serpre = Messages(message=pre,name="server" + json['user_name'])

		elif preintend(json['message'], json['user_name']) == 'ques':
			pre, serpre = get3answer(json)

	elif guive[json['user_name']]['state'] == 1:
		pre, serpre = handle3cauhoi(json)
	elif guive[json['user_name']]['state'] == 2:
		pre, serpre = handletree(json)
	elif guive[json['user_name']]['state'] == 3:
		pre, serpre = handle3cauhoi(json)

	#elif guive[json['user_name']]['state'] == 2:


			# pre = 'Có phải bạn muốn hỏi: ' + predict(str(json['message']), json['user_name'])
	# serpre = Messages(message=pre,name="server")


	db.session.add(serpre)
	db.session.commit()
	x =  { "user_name":"server" + json['user_name'], "message":pre }
	print('received my event: ' + str(x))
	socketio.emit( 'my response', json, callback=messageReceived)
	socketio.emit( 'my response', x, callback=messageReceived)


if __name__ == '__main__':
    socketio.run(app, debug=False)






