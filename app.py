from flask import *
import mysql.connector

app=Flask(__name__, static_url_path="/", static_folder="image")
app.config["JSON_AS_ASCII"]=False
app.config["TEMPLATES_AUTO_RELOAD"]=True

app.config['JSON_SORT_KEYS'] = False

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


app.run(host="0.0.0.0", port=3000)