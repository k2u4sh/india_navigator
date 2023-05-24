# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""
import pandas as pd
from sqlalchemy import create_engine, MetaData,Table, Column, Numeric, Integer, VARCHAR,Float, Date,update,insert
from django import template
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.urls import reverse
from django.shortcuts import render
from .forms import UploadForm
from django.http import HttpResponse
import mysql.connector
import openpyxl
import datetime as dt


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


@login_required(login_url="/login/")
def index(request):
    context = {'segment': 'index'}

    html_template = loader.get_template('home/index.html')
    return HttpResponse(html_template.render(context, request))


@login_required(login_url="/login/")
def pages(request):
    context = {}
    # All resource paths end in .html.
    # Pick out the html file name from the url. And load that template.
    try:

        load_template = request.path.split('/')[-1]

        if load_template == 'admin':
            return HttpResponseRedirect(reverse('admin:index'))
        context['segment'] = load_template

        html_template = loader.get_template('home/' + load_template)
        return HttpResponse(html_template.render(context, request))

    except template.TemplateDoesNotExist:

        html_template = loader.get_template('home/page-404.html')
        return HttpResponse(html_template.render(context, request))

    except:
        html_template = loader.get_template('home/page-500.html')
        return HttpResponse(html_template.render(context, request))
    


def upload_user(request):
    if request.method == "POST":
        handle_uploaded_file(request.FILES['file'])  
        return HttpResponse("File uploaded successfuly")  
    else :
        student = UploadForm()  
        return render(request,"home/forms.html",{'form':student})  

def handle_uploaded_file(f): 
    with open('staticfiles/upload/'+f.name, 'wb+') as destination:  
        for chunk in f.chunks():  
            destination.write(chunk)

    test = read_content_1(f)
    return test

def read_content_1(f):
    df = pd.read_excel(r'staticfiles/upload/'+f.name+'', sheet_name='State Care')
    dfa = pd.read_excel(r'staticfiles/upload/'+f.name+'', sheet_name='ISGS')

    content=pd.read_excel(r'staticfiles/upload/'+f.name+'', sheet_name='Generation', skiprows=4, usecols="C", nrows=1, header=None, names=["Value"]).iloc[0]["Value"]

    data = df.iloc[5:44, 1:5]
    data1 = dfa.iloc[5:129, 1:9]

   # Cleaning the Dataframe

   # Renaming column names
    data.rename(columns = {'Central Electricity Authority/ केन्द्रीय विद्युत प्राधिकरण':'states', 'Unnamed: 2': 'wind', 'Unnamed: 3':'solar', 'Unnamed: 4':'others', 'Unnamed: 5':'dates' }, inplace = True)
    data1.rename(columns = {'Central Electricity Authority/ केन्द्रीय विद्युत प्राधिकरण':'stations', 'Unnamed: 2': 'state', 'Unnamed: 3':'sector', 'Unnamed: 4':'owner', 'Unnamed: 5':'type', 'Unnamed: 6':'icap', 'Unnamed: 7':'agen' , 'Unnamed: 8':'cgen', 'Unnamed: 9':'dates'  }, inplace = True)

   # Dropping Regions
    data.drop(data.index[[10, 18, 31]], inplace=True)
    # data1.drop(data.index[84, 106, 58,[]], inplace=True)
   
   # Removing Hindi Characters
    temp = data["states"].to_list()

    for i in range(len(temp)):
      temp[i] = temp[i].split('/')[1]
      if temp[i][0] == ' ':
        temp[i] = temp[i][1:]
      if temp[i][-1] == '':
        temp[i] == temp[i][:len(temp[i]) - 1]
    data['states'] = temp
    data['dates'] = content
    data1['dates'] = content

    # Convert dataframe to sql table                                   
    data.to_sql('data', engine,if_exists='append',index=False)
    data1.to_sql('station_data', engine,if_exists='append',index=False)
    states=getstates()
    totalsolar,intersolar,intrasolar = solar(states.name,content)
    totalwind,interwind,intrawind = wind(states.name,content)
    totalGraphWind = totalsolar + totalwind

    sql = """INSERT INTO  final_data (date,wind,solar,wind_inter,wind_intra,solar_inter,solar_intra,wind_graph) VALUES (%s, %s,%s,%s,%s,%s,%s,%s)"""
    val = (content,totalwind,totalsolar,interwind,intrawind,intersolar,intrasolar,totalGraphWind)
    mycursor.execute(sql, val)
    mydb.commit()
    return 1


def getstates():
    sql = "select * from states"
    states = pd.read_sql(sql,con=engine)
    return states



def solar(dta,date):
    solard = []
    solarloc = [] 
    date = str(date).strip(" ")
    sumSolarInter = 0
    sumSolarIntra = 0
    # if len(dateArray) > 0:
    #   for date in dateArray:
    if len(dta) > 0:
       for solarData in dta:
            solarInner = "select solar from data where states = '"+solarData+"' and dates = '"+date+"'"
            solar_intrastate = pd.read_sql(solarInner,con=engine)
            intrastate_value = solar_intrastate.solar[0]
            solarIntrsa = "select project_name,percentage from project_offtaker where state = '"+solarData+"'"
            solarIntra = pd.read_sql(solarIntrsa,con=engine)
            intr = []
            intra = 0
            for index, item in enumerate(solarIntra.project_name):
               project_wisedata = "select agen from station_data where stations = '"+item+"'"
               solars_act = pd.read_sql(project_wisedata,con=engine)
               prcentage_cal = float(solars_act.agen[0]) * float(solarIntra.percentage[index])
               intr.append(float(prcentage_cal))  
               if len(intr) == len(solarIntra.project_name):
                  intra = sum(intr)
                  
            loc_data = {"date":date,"location":solarData,"tech":"solar","intrastate":intrastate_value,"interstate":intra}
            sql = """INSERT INTO graph_data (date,location,tech,intrastate,interstate) VALUES (%s, %s,%s,%s,%s)"""
            val = (date,solarData,"solar",intrastate_value,intra)
            mycursor.execute(sql, val)
            mydb.commit()
            sumSolarInter = float(intrastate_value) + float(sumSolarInter)
            sumSolarIntra = float(intra) + float(sumSolarIntra)

            solarloc.append(loc_data)
            if len(solarloc) == len(dta):
                totalSolar = sumSolarInter + sumSolarIntra
                return totalSolar,sumSolarInter,sumSolarIntra
               
            #    solardd = {"solar":solarloc}
            #    solard.append(solardd)
            #    if len(solard) == len(dateArray):
                   


def wind(dta,date):
    solard = []
    solarloc = [] 
    # if len(dateArray) > 0:
    #   for date in dateArray:
    date = str(date).strip(" ")
    sumWindInter = 0
    sumWindIntra = 0
    if len(dta) > 0:
       for solarData in dta:
            solarInner = "select solar from data where states = '"+solarData+"' and dates = '"+date+"'"
            solar_intrastate = pd.read_sql(solarInner,con=engine)
            intrastate_value = solar_intrastate.solar[0]
            solarIntrsa = "select project_name,percentage from project_offtaker where state = '"+solarData+"'"
            solarIntra = pd.read_sql(solarIntrsa,con=engine)
            intr = []
            intra = 0
            for index, item in enumerate(solarIntra.project_name):
               project_wisedata = "select agen from station_data where stations = '"+item+"'"
               solars_act = pd.read_sql(project_wisedata,con=engine)
               prcentage_cal = float(solars_act.agen[0]) * float(solarIntra.percentage[index])
               intr.append(float(prcentage_cal)) 
               if len(intr) == len(solarIntra.project_name):
                  intra = sum(intr)
                  
            loc_data = {"date":date,"location":solarData,"tech":"wind","intrastate":intrastate_value,"interstate":intra}
            sql = """INSERT INTO graph_data (date,location,tech,intrastate,interstate) VALUES (%s, %s,%s,%s,%s)"""
            val = (date,solarData,"wind",intrastate_value,intra)
            mycursor.execute(sql, val)
            mydb.commit()
            sumWindInter = float(intrastate_value) + float(sumWindInter)
            sumWindIntra = float(intra) + float(sumWindIntra)

            solarloc.append(loc_data)
            if len(solarloc) == len(dta):
                totalWind = float(sumWindInter) + float(sumWindIntra)
                return totalWind,sumWindInter,sumWindIntra


    
