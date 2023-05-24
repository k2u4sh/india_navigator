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
hostname="localhost"
dbname="usco"
uname="root"
pwd=""
engine = create_engine("mysql+pymysql://{user}:{pw}@{host}/{db}"
				.format(host=hostname, db=dbname, user=uname, pw=pwd))


mydb = mysql.connector.connect(
  host=hostname,
  user=uname,
  password="",
  database=dbname
)


mycursor = mydb.cursor()


@api_view(('GET',))
def getApiValue(request):
   if request.method == "GET":
      #   location =  request.GET.get("location")
      #   type =  request.GET.get("type")
        sql = "select * from final_data"
        graph = pd.read_sql(sql,con=engine)
        datasets = []
        data=[]
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
        
        data = {"data":data}
        return Response(data,status=status.HTTP_200_OK)
   

                    
                  

@api_view(('GET',))
def getStates(request):
   if request.method == "GET":
      df = pd.read_sql("SELECT * FROM states", con = engine)
      return Response(df.name,status=status.HTTP_200_OK)





