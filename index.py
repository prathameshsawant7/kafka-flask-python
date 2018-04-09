from flask import Flask, render_template, request
from kafka import SimpleProducer, KafkaClient
import sqlite3
import sys
import json

app 	= Flask(__name__)
conn 	= sqlite3.connect('missionExecute.db')


@app.route('/')
def index():
	data = {}
	cursor 		= conn.execute("SELECT * FROM transaction_logs ORDER BY log_id DESC LIMIT 100")
	userRows 	= cursor.fetchall()
	data['userData'] = userRows

	cursor 		= conn.execute("SELECT DISTINCT user_id FROM transaction_logs")
	userList 	= cursor.fetchall()
	data['userList'] = userList

	return render_template('index.html',data=data)

@app.route('/getUserData', methods=['POST'])
def getUserData():
	data 		= {}
	dataJson	= request.get_json()
	dataArr 	= json.loads(dataJson)
	user_id 	= dataArr['user_id']
	cursor 		= conn.execute("SELECT * FROM transaction_logs WHERE user_id = ? ORDER BY log_id",(user_id,))
	userList    = cursor.fetchall()
	data['userData'] = userList
	return render_template('getUserData.html',data=data)

@app.route('/addTransaction', methods=['POST'])
def addTransaction():
	kafka 				= KafkaClient('localhost:9092')
	producer 			= SimpleProducer(kafka)
	topic 				= 'transQueue'
	data 		 		= {}
	data['user_id']     = request.form['user_id']
	data['dateField']	= request.form['trans_date']
	data['trans_type']	= request.form['trans_type']
	data['trans_amt']	= request.form['trans_amt']
	dataJson 			= json.dumps(data, separators=(',',':'))
	producer.send_messages(topic,dataJson)
	return 'Transaction added to queue';

if __name__ == '__main__':
	app.run()