import urllib.request as request
import json
import mysql.connector

#資料庫連線
mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="qaz4545112",
  database="website"
)

#讀檔
path = "D://training/git/project-1/taipei-day-trip-website/data/taipei-attractions.json"
with open(path, encoding="utf-8") as json_file:
    data = json.load(json_file)
lst = data["result"]
#print(lst[0])


for val in lst["results"]:    

    #欄位要排除不是jpg或png的網址 
    li = str(val["file"]).split("http")
    #print("aaaa: "+li[1])
    src=""
    for j in li:
        if(j.find("jpg")!=-1 or j.find("JPG")!=-1 or j.find("png")!=-1 or j.find("PNG")!=-1):
            src += "http" + j

    #insert 資料到資料庫
    with mydb.cursor() as cursor:        
        sql = "Insert Into travel (info, stitle, xpostDate, longitude, REF_WP, avBegin, langinfo, MRT, SERIAL_NO, RowNumber, CAT1, CAT2, MEMO_TIME, POI, file, idpt, latitude, xbody, _id, avEnd, address) Values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)" 
        val = (val["info"], val["stitle"], val["xpostDate"], val["longitude"], val["REF_WP"], val["avBegin"], val["langinfo"], val["MRT"], val["SERIAL_NO"], val["RowNumber"], val["CAT1"], val["CAT2"], val["MEMO_TIME"], val["POI"], src, val["idpt"], val["latitude"], val["xbody"], val["_id"], val["avEnd"], val["address"])   
        cursor.execute(sql, val)
        mydb.commit()   

print("完成")


