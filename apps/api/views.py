# todo/api/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions
from rest_framework.decorators import api_view, renderer_classes
from sqlalchemy import create_engine, MetaData,Table, Column, Numeric, Integer, VARCHAR,Float, Date,update,insert
import pandas as pd
import mysql.connector

# Credentials to database connection
hostname="erekrut-beta.c1uzvjtqk2xu.ap-south-1.rds.amazonaws.com"
dbname="navigator"
uname="root"
pwd="po98#2hy$678G"

engine = create_engine("mysql+pymysql://{user}:{pw}@{host}/{db}"
				.format(host=hostname, db=dbname, user=uname, pw=pwd))

mydb = mysql.connector.connect(
  host=hostname,
  user=uname,
  password=pwd,
  database=dbname
)


mycursor = mydb.cursor()


@api_view(('GET',))
def getApiValue(request):
   if request.method == "GET":
        startDate =  request.GET.get("startDate")
        lastDate =  request.GET.get("lastDate")
        sql = "select * from final_data WHERE date BETWEEN '"+startDate+"' AND '"+lastDate+"'"
        graph = pd.read_sql(sql,con=engine)

        mycursor.execute(sql)
        myresult = mycursor.fetchall()
        datasets = []
        data=[]
        graphD = []
        labels = graph.date
        data_solar = graph.solar
        data_wind = graph.wind_graph
        dataSet_Solar = {"fill":{"target": "origin","above": "rgba(255, 0, 0, 0.4)","below": "rgba(0, 0, 255, 0.4)"},"label":"Solar","data":data_solar,"borderWidth": 1}
        dataSet_wind = {"fill":{"target": "origin","above": "rgba(255, 0, 0, 0.4)","below": "rgba(0, 0, 255, 0.4)"},"label":"Wind","data":data_wind,"borderWidth": 1}
      #   dataSet_other = {"fill":{"target": "origin","above": "rgba(255, 0, 0, 0.4)","below": "rgba(0, 0, 255, 0.4)"},"label":"Others","data":df.others,"borderWidth": 1}
        datasets.append(dataSet_Solar)
        datasets.append(dataSet_wind)
      #   datasets.append(dataSet_other)
        
        s = {"labels":labels,"datasets":datasets}
        data.append(s)

        if len(myresult) > 0:
            for x in myresult:
                gd = {"date":x[8],"wind":x[1],"solar":x[2],"interstatewind":[3],"intrastatewind":[4],"interstatesolar":[5],"intrastatesolar":[6]}
                graphD.append(gd)
                if len(graphD) == len(myresult):
                    data = {"data":data,"datagraph":graphD}
                    return Response(data,status=status.HTTP_200_OK)
        else:
           data = {"data":data,"datagraph":graphD}
           return Response(data,status=status.HTTP_200_OK)
   

                    
                  

@api_view(('GET',))
def getStates(request):
   if request.method == "GET":
      df = pd.read_sql("SELECT * FROM states", con = engine)
      return Response(df.name,status=status.HTTP_200_OK)





