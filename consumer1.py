from kafka import KafkaConsumer,KafkaProducer,TopicPartition
import sqlite3
import json
import numpy as np
import datetime
import threading, time

class Consumer(threading.Thread):
	global monthMapping
	daemon 		= True
	monthMapping = {
		'01':'JAN',
		'02':'FEB',
		'03':'MAR',
		'04':'APR',
		'05':'MAY',
		'06':'JUN',
		'07':'JUL',
		'08':'AUG',
		'09':'SEP',
		'10':'OCT',
		'11':'NOV',
		'12':'DEC'
	}

	def __init__(self, num):
		
		threading.Thread.__init__(self)
		self.consumer = KafkaConsumer(bootstrap_servers=['localhost:9092'],
								 group_id='transQueue',
								 client_id='transQueue')
		self.consumer.assign([TopicPartition('transQueue',num)])
		
		self.run(num)
 
	def run(self,num):
		conn = sqlite3.connect('missionExecute.db')
		for message in self.consumer:
			print(message.value)
			row = json.loads(message.value)
			user_id 	= row['user_id']
			month 		= [key for key, value in monthMapping.iteritems() if value == row['dateField'][2:5].upper()][0]
			dateField	= (row['dateField'][5:]+"-"+month+"-"+row['dateField'][:2])
			trans_type  = row['trans_type']
			trans_amt   = row['trans_amt']
			cursor 		= conn.execute("SELECT trans_type,trans_amt,total_balance FROM transaction_logs WHERE user_id=?;",(user_id,))
			userRows 	= cursor.fetchall()
			total_balance = 0
			mark 	= 0
			std     =[]
			amtD	=[]
			amtC	=[]
			for userRow in userRows:
				total_balance = (total_balance+userRow[1]) if userRow[0] == 'C' else (total_balance-userRow[1])
				if trans_type == 'C':
					amtC.append(userRow[1])
				elif trans_type == 'D':
					amtD.append(userRow[1])

			if trans_type == 'C':
				amtC.append(trans_amt)
				total_balance += int(trans_amt)
			elif trans_type == 'D':
				amtD.append(trans_amt)
				total_balance -= int(trans_amt)
			
			stdarr = np.array(amtC) if trans_type == 'C' else np.array(amtD) if trans_type == 'D' else 0
			
			if len(stdarr) > 1:
				std = np.std(stdarr.astype(np.int)) 
			else:
				std = 1
			mark = 1 if std > 1 else 0
			conn.execute("INSERT INTO transaction_logs (user_id,trans_date,trans_type,trans_amt,total_balance,trans_std,marked_trans,created_at) VALUES (?,?,?,?,?,?,?,?)",(user_id,dateField,trans_type,trans_amt,total_balance,std,mark,datetime.datetime.now(),))
			conn.commit()

if __name__ == "__main__":
	threads = [
		Consumer(0),
		Consumer(1)
	]
	for t in threads:
		t.start()
	while True:
		time.sleep(10)