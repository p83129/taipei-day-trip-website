from logging import NullHandler
from os import times
import re
from flask import *
import mysql.connector

from flask import request
from flask import render_template
from flask import url_for
from flask import redirect
from datetime import date, datetime
import requests
import urllib.request
import json 


app=Flask(__name__, static_url_path="/", static_folder="image")
app.config["JSON_AS_ASCII"]=False
app.config["TEMPLATES_AUTO_RELOAD"]=True

app.config['JSON_SORT_KEYS'] = False

app.secret_key = b'p83129'

# Pages
@app.route("/")
def index():
	return render_template("index.html")
@app.route("/attraction/<id>")
def attraction(id):
	return render_template("attraction.html")
@app.route("/booking")
def booking():
	return render_template("booking.html")
@app.route("/thankyou")
def thankyou():
	return render_template("thankyou.html")


mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="qaz4545112",
  database="website"
)

@app.route("/api/attractions",methods=["GET"])
def api_attractions():
	page = request.args.get("page", "0")
	keyword = request.args.get("keyword")
	#print(keyword)

	sql = ""
	val = ""		
	data_info = ""
	jsObj = ""
	num = 0
	#result

	#分頁運算
	Pagecount = 12		
	firstPage = 0
	#lastPage = 12
	if int(page) > 0:
		firstPage = (int(page) * Pagecount)
		#lastPage = (lastPage *int(page)) + Pagecount
	
	with mydb.cursor() as cursor:		

		if(keyword == "" or keyword == None):			
			sql = "Select Count(*) From travel"
		else:
			sql = "Select Count(*) From travel Where stitle Like '%" + keyword + "%'"        

		cursor.execute(sql)
		count = cursor.fetchall()

		for c in count:
			num = int(c[0])

		mydb.close #關資料庫
		
	with mydb.cursor() as cursor:
		if(keyword == "" or keyword == None):
			#sql = "Select _id, stitle, CAT2, xbody, Address, info, MRT, latitude, longitude, file From travel "				
			sql = "Select _id, stitle, CAT2, xbody, Address, info, MRT, latitude, longitude, file From travel Limit " + str(firstPage) + ", 12"
		else:
			#sql = "Select _id, stitle, CAT2, xbody, Address, info, MRT, latitude, longitude, file From travel Where stitle Like '%" + keyword + "%'"
			sql = "Select _id, stitle, CAT2, xbody, Address, info, MRT, latitude, longitude, file From travel Where stitle Like '%" + keyword + "%' Limit " + str(firstPage) + ", 12"        
			#val = (keyword,)
		#print("~~~~~~~~~~~~~~~~~~~~~~", sql)
		cursor.execute(sql)
		result = cursor.fetchall()
		mydb.close #關資料庫



		#總頁數			
		totalPage = int(num/Pagecount)
		#print("總頁數", str(totalPage))
		#print("nnnnnnnnnnnn", str(num))

		
		if(len(result) > 0 and int(page) <= totalPage):
			json_array =[]


			#for row in result[firstPage:lastPage]:
			for row in result:
				img=""
				json_list = {}

				id = str(row[0])				
				name = str(row[1])
				category = str(row[2])
				description = str(row[3])
				address = str(row[4])
				transport = str(row[5])
				mrt = str(row[6])
				latitude = str(row[7])
				longitude = str(row[8])
				images = str(row[9]).split('http')
				
				#print("5555" ,name)
				
				for i in images[1:]:
					img += 'http'+ i +","
				img = img.strip(',')				

				json_list['id'] = id
				json_list['name'] = name
				json_list['category'] = category
				json_list['description'] = description
				json_list['address'] = address
				json_list['transport'] = transport
				json_list['mrt'] = mrt
				json_list['latitude'] = latitude
				json_list['longitude'] = longitude
				json_list['images'] = [img]

				json_array.append(json_list)
			
			
			
			if int(page) < totalPage:
				nextPage = int(page) + 1
				data_info = {'nextPage':nextPage,
							'data': 
								json_array								
						}	
			else:				
				data_info = {'nextPage':None,
							'data': 
								json_array								
						}	
				

			jsObj = jsonify(data_info) 
			#return jsObj
				  
				
		else:
			#出錯誤訊息
			Error_info = {
				'error':True,
				'message':"查無此景點或超過查詢頁數"
			} 
			jsObj = jsonify(Error_info)
				
		
		return jsObj

@app.route("/api/attraction/<attractionId>",methods=["GET"])
def api_attractions_id(attractionId):
	id = attractionId

	if id.isdigit():#判斷是否為數字
		
		with mydb.cursor() as cursor:
			img = ""
			jsObj = ""

			sql = "Select _id, stitle, CAT2, xbody, Address, info, MRT, latitude, longitude, file From travel Where _id = '" + id + "'"  
			cursor.execute(sql)
			result = cursor.fetchall()

			mydb.close #關資料庫

			if len(result)>0:
				for row in result:
					images = str(row[9]).split('http')				
					for i in images[1:]:
						img += 'http'+ i +","
					img = img.strip(',')			

					data_info = {'data': 
									{
										'id': str(row[0]),
										'name': str(row[1]),
										'category': str(row[2]),
										'description': str(row[3]),
										'address': str(row[4]),
										'transport': str(row[5]),
										'mrt': str(row[6]),
										'latitude': str(row[7]),
										'longitude': str(row[8]),
										'images': [img]
									}
								}	
					jsObj = jsonify(data_info)
					return jsObj
			else: #400錯誤訊息
				Error_info = {
					'error':True,
					'message':"查無此景點編號"
				} 
				jsObj = jsonify(Error_info)				
		
				return jsObj
					
	else: #500錯誤訊息
		Error_info = {
			'error':True,
			'message':"景點編號輸入異常"
		} 
		jsObj = jsonify(Error_info)				
		
		return jsObj

@app.route("/api/user",methods=["GET"])
def api_user_get():	
	#print("0000000000000000000000000000000000000",str(session['id']))
	#print("0000000000000000000000000000000000000",session['id'])
	try:
		id = session['id']
		name = session['name']
		email = session['email']
		
		if name !="" and email !="" and id !="":
			data_info = {'data':{
									'id':id,
									'name':name,
									'email':email
								}
						}							
			jsObj = jsonify(data_info)				
			return jsObj
		else:
			data_info = {'data':None}
			jsObj = jsonify(data_info)				
			return jsObj
	#session抓不到值
	except:
		data_info = {'data':None}
		jsObj = jsonify(data_info)				
		return jsObj

@app.route("/api/user",methods=["POST"])
def api_user_post():
	#print("4564567845121456123")
	# Name = request.args.get("txtName_new")
	# Email = request.args.get("txtEmail_new")
	# Password = request.args.get("txtPassword_new")
	data = json.loads(request.data)
	Name = str(data['name'])
	Email = str(data['email'])
	Password = str(data['password'])
	
	try:
		with mydb.cursor() as cursor:
			sql = "Select name From user Where email = '"  + Email + "'"
			print(sql)
			cursor.execute(sql)
			result = cursor.fetchall()
			mydb.close #關資料庫
			#print("123132132131132123132")
			if len(result)==0:					
				sql = "Insert Into user (name, email, password) Values(%s, %s, %s)" 
				val = (Name, Email, Password)   
				cursor.execute(sql, val)
				mydb.commit()
				mydb.close #關資料庫
				#print("新增")
				data_info = {'ok':True}
				jsObj = jsonify(data_info) 					
				return jsObj

			else:
				data_info = {'error':True, 'message':"此電子信箱已註冊過"}
				jsObj = jsonify(data_info) 					
				return jsObj

	except:
		data_info = {'error':'true',
					'message':'伺服器內部錯誤'}
		jsObj = jsonify(data_info) 		
		return jsObj

@app.route("/api/user",methods=["PATCH"])
def api_user_patch():	
	#Email=request.form["txtEmail"]
	#Password=request.form["txtPassword"]
	# Email = request.args.get("txtEmail")
	# Password = request.args.get("txtPassword")
	data = json.loads(request.data)
	Email = str(data['email'])
	Password = str(data['password'])
	#print("!!!!!!!!!!!!!!!!!!!!!!!", Email)
	try:
		with mydb.cursor() as cursor:
			sql = "Select id, name From user Where email = '"  + Email + "' And password = '" + Password + "'"		
			cursor.execute(sql)
			result = cursor.fetchall()
			mydb.close #關資料庫
			
			if len(result)>0:
				for row in result:							
					#print("~~~~~~~~~~")
					session['status'] = '已登入' 
					session['id'] = str(row[0])
					session['name'] = str(row[1])
					session['email'] = Email
					session['password'] = Password
					#print("session", session['name'])					
					data_info = {'ok':True}
					jsObj = jsonify(data_info) 					
					return jsObj
					
			else:
				#print("elseelseelseleselselslelsel")
				data_info = {'error':True,
							'message':"帳號或密碼錯誤"}
				jsObj = jsonify(data_info)				
				return jsObj
					
	except:
		data_info = {'error':'true',
					'message':'伺服器內部錯誤'}
		jsObj = jsonify(data_info) 		
		return jsObj

@app.route("/api/user",methods=["DELETE"])
def api_user_delete():
	session['status'] = "已登出" 
	session['email'] = ""
	session['password'] = ""

	data_info = {'ok':True}
	jsObj = jsonify(data_info) 		
	return jsObj

@app.route("/api/booking",methods=["GET"])
def api_booking_get():
	data_info = ""
	img = []
	try:
		# if session['status'] == None:
		# 	print("1231231321321321231465465")
		# else: 
		# 	print("錯誤")
		if session['status'] == "已登入":		
			with mydb.cursor() as cursor:
				sql = "Select A._id, A.stitle, A.Address, A.file, B.date, B.time, B.price From travel AS A left join booking AS B on(A._id = B.attractionId) Where B.Email = '"+session['email'] + "'"
				#sql = "Select A._id, A.stitle, A.Address, A.file, B.date, B.time, B.price From travel AS A left join booking AS B on(A._id = B.attractionId) Where B.Email = %s"
				#val = (session['email'])			
				cursor.execute(sql)
				result = cursor.fetchall()		
				
				if(len(result) >0):
					for row in result:
						images = str(row[3]).split('http')	

					#把圖片切割依序放在陣列					
					for i in images[1:]:
						img.append('http'+ i)					
					#print("000000000000000000000000000", img)	
							
					data_info = {'data': {						
									'attraction':{
										'id': str(row[0]),
										'name': str(row[1]),											
										'address': str(row[2]),											
										'image': img[0]
									}
								},
								'date':str(row[4]),
								'time':str(row[5]),
								'price':str(row[6])
							}
					jsObj = jsonify(data_info)				
					return jsObj

				else:
					data_info = {'data':None}
					jsObj = jsonify(data_info)				
					return jsObj	

		else:
			data_info = {'error':True,
						'message':"請先登入會員"}
			jsObj = jsonify(data_info)				
			return jsObj
	except:
		data_info = {'error':True,
						'message':"請先登入會員"}
		jsObj = jsonify(data_info)				
		return jsObj

@app.route("/api/booking",methods=["POST"])
def api_booking_post():
	# id = request.args.get("id")
	# date = request.args.get("txtdate")
	# time = request.args.get("txttime")
	# price = request.args.get("txtmoney")
	data = json.loads(request.data)
	id = str(data['attractionId'])
	date = str(data['date'])
	time = str(data['time'])
	price = str(data['price'])	
	count = 0
	jsObj = ""
	
	try:
		if session['status'] == "已登入":
			with mydb.cursor() as cursor:				

					sql = "Select Email From booking Where Email = '" + session['email'] + "'"  					
					cursor.execute(sql)
					result = cursor.fetchall()				

					if len(result)>0:
						sql = "Update booking Set attractionId = %s, date = %s, time = %s, price = %s Where Email = %s " 				
						val = (id, date, time, price, session['email'])
						cursor.execute(sql, val)
						mydb.commit()
						count = cursor.rowcount #回傳成功筆數
						#print("update: ", count)
						mydb.close #關資料庫
					else:
						sql = "Insert Into booking(Email, attractionId, date, time, price) Values(%s, %s, %s, %s, %s) " 				
						val = (session['email'], id, date, time, price)
						cursor.execute(sql, val)
						mydb.commit()
						count = cursor.rowcount #回傳成功筆數
						#print("insert: ", count)
						mydb.close #關資料庫

					if count > 0:
						data_info = {'ok':True}
						jsObj = jsonify(data_info)
						return jsObj
					else:
						data_info = {'error':True,
						'message':'請勿重複預定行程'}
						jsObj = jsonify(data_info)
						return jsObj
		else:
			data_info = {'error':True,
						'message':"請先登入會員"}
			jsObj = jsonify(data_info)				
			return jsObj

	except:
		data_info = {'error':True,
					'message':"伺服器內部錯誤"}
		jsObj = jsonify(data_info)				
		return jsObj

@app.route("/api/booking",methods=["DELETE"])
def api_booking_delete():
	if session['status'] == "已登入":
		with mydb.cursor() as cursor:
			sql = "Delete From booking Where Email = '" + session['email'] + "'"
			#val = (session['email'])		
			cursor.execute(sql)		
			mydb.commit()	
			mydb.close #關資料庫

		data_info = {'ok':True}
		jsObj = jsonify(data_info)
		return jsObj
		
	else:
		data_info = {'error':True,
					'message':"請先登入會員"}
		jsObj = jsonify(data_info)				
		return jsObj

@app.route("/api/orders",methods=["POST"])
def api_orders_post():	
	data = json.loads(request.data)	
	#print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~", data)
	prime = str(data['prime'])
	price = int(data['order']['price'])	
	phone = str(data['order']['contact']['phone'])
	name = str(data['order']['contact']['name'])
	email = str(data['order']['contact']['email'])
	attractionID = str(data['order']['trip']['attraction']['id'])
	date = str(data['order']['trip']['date'])
	time = str(data['order']['trip']['time'])
	# prime = request.args.get("prime")
	# phone = request.args.get("phone")
	orderNumber = datetime.now().strftime('%Y%m%d%H%M%S%f') #訂單編號用當前時間來命名
	#print("~~~~~~~~~~~~~~~~~~~~~", orderNumber)
	status = 0
	message = ""
	try:
		if session['status']=='已登入':		

			if orderNumber!=None:				
				
				if data != None:					
					#串TapPay 的API
					tappay_json={'prime':prime,
						'partner_key':"partner_hN0LQnBJwfXVeKxxAsiNLUg6ZqaKOmqnZlngMFucyEOIBmTy0Un0rEGg",
						'merchant_id':"p83120911_TAISHIN",
						'details':"TapPay Test",
						'amount':price,
						'order_number':orderNumber,
						'cardholder':{
							'phone_number':phone,
							'name':name,
							'email':email									
						},
						'remember':True
					}

					body = str.encode(json.dumps(tappay_json))
					# print("2222222222222222222222222",body)
					url = "https://sandbox.tappaysdk.com/tpc/payment/pay-by-prime"					
					headers = {'Content-Type':'application/json','x-api-key':'partner_hN0LQnBJwfXVeKxxAsiNLUg6ZqaKOmqnZlngMFucyEOIBmTy0Un0rEGg'}

					req = urllib.request.Request(url, body, headers)
					
					try:						
						response = urllib.request.urlopen(req)
						result = response.read()
						obj = json.loads(str(result,encoding='UTF-8'))								
						#print("777777777777777777777777777777", obj['status'])
						status = obj['status']
						if status == 0:
							message = "付款成功"
						else:
							message = "付款失敗"

					except urllib.request.HTTPError as error: 
						print("The request failed with status code: " + str(error.code))
						
						print("55555555555",error.info())
						print("66666666666666",json.loads(error.read())) 


					#insert 訂單到資料庫中
					with mydb.cursor() as cursor:
						sql = "Insert Into orders(email, phone, price, attractionID, date, time, status, orderNumber) Values(%s, %s, %s, %s, %s, %s, %s, %s)" 
						val = (email, phone, price, attractionID, date, time, status, orderNumber)   
						cursor.execute(sql, val)
						mydb.commit()
						mydb.close #關資料庫
						count = cursor.rowcount #回傳成功筆數
						#print("insert: ", count)					

				data_info = {'data':{
						'number':orderNumber,
						'payment':{
							'status':status,
							'message':message
						}
					}
				}
				
				jsObj = jsonify(data_info)				
				return jsObj	
			else:
				data_info = {'error':True,
					'message':"建立訂單失敗"}
				jsObj = jsonify(data_info)				
				return jsObj	

		else:
			data_info = {'error':True,
						'message':"請先登入會員"}
			jsObj = jsonify(data_info)				
			return jsObj
	except:
		data_info = {'error':True,
						'message':"伺服器內部錯誤"}
		jsObj = jsonify(data_info)				
		return jsObj

@app.route("/api/order/<orderNumber>",methods=["GET"])
def api_order_get(orderNumber):	
	# print("111111111111111111111111111111111145646465")
	img = []
	
	if session['status']=='已登入':
		with mydb.cursor() as cursor:	
			sql = """	Select A.price, A.attractionId, A.date, A.time, B.stitle, B.address, B.file, C.name, C.email, D.phone, D.status, D.orderNumber
						From booking AS A 
							left join travel AS B on(A.attractionId = B._id)
							left join user AS C on(A.Email = C.Email)
							left join orders AS D on(A.Email = D.Email)
						Where D.orderNumber = '""" + orderNumber + "'" 			
			cursor.execute(sql)
			result = cursor.fetchall()
			mydb.close #關資料庫

			if len(result) >0:
				for row in result:
					images = str(row[6]).split('http')	
					#把圖片切割依序放在陣列					
					for i in images[1:]:
						img.append('http'+ i)

					
					data_info = {'data':{
							'number': orderNumber,
							'price':str(row[0]),
							'trip':{
								'attraction':{
									'id':str(row[1]),
									'name':str(row[4]),
									'address':str(row[5]),
									'image':img[0]
								},
								'date':str(row[2]),
								'time':str(row[3])
							},
							'contact':{
								'name':str(row[7]),
								'email':str(row[8]),
								'phone':str(row[9])
							},
							'status':str(row[10])
						}
					}
							
					jsObj = jsonify(data_info)	
					# print("2222222222222222222222222222222222456465489")			
					return jsObj
			else:
				data_info = {"data": None}
				jsObj = jsonify(data_info)	
				return jsObj
	else:
		data_info = {'error':True,
						'message':"請先登入會員"}
		jsObj = jsonify(data_info)				
		return jsObj




app.run(host="0.0.0.0", port=3000)