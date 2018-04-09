import csv
import sys
import json
from kafka import SimpleProducer, KafkaClient

class publish():
	def getData(self,path):
		kafka 		= KafkaClient('localhost:9092')
		producer 	= SimpleProducer(kafka)
		topic 		= 'transQueue'
		with open(path) as File:  
		    reader = csv.reader(File)
		    count = 0
		    for row in reader:
		    	count += 1
		    	if count != 1:
		    		data = {}
		    		data['user_id']		=	row[0]
		    		data['dateField']	=	row[1]
		    		data['trans_type']	=	row[2]
		    		data['trans_amt']	=	row[3]
		    		dataJson 			= 	json.dumps(data, separators=(',',':'))
		    		producer.send_messages(topic,dataJson)
		    		print(dataJson)


if __name__ == "__main__":
	print("Enter file name: ")
	path = raw_input()
	run = publish()
	run.getData(path)