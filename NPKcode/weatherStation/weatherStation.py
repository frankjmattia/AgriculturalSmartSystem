# -*- coding: utf-8 -*-
import time
from pinpong.board import Board, UART
import siot
import os

#Unihiker Initialize
Board("UNIHIKER").begin()  

#UART P0-RX P3-TX ,pls note that weather station's baud_rate is 9600
uart1 = UART()   
uart1.init(baud_rate = 9600, bits=8, parity=0, stop = 1) 
#siot init and connect to the LP server. The server's IP is 10.168.1.100. 
#pls note that each unihiker's client_id is different. 
siot.init(client_id="weatherstation",server="10.168.1.100",port=1883,user="siot",password="dfrobot")
while True:
    databuffer = ""
    #print(len("c000s000g000t082r000p000h48b10022*3C"))default buffer
    #read uart data
    buf = uart1.readline()

    if buf is None:
        print("recv None")
    else:
        for i in buf:
            #print(i)
            a = chr(i)
            databuffer = databuffer + a

        length = len(databuffer)
        print(databuffer)
        if length == 38:  
            print("databuffer:",databuffer)
            
            '''get wind direction'''
            try:
                WindDirection = int(databuffer[1:4])
            except:
                WindDirection = 0
            
            if 0 <= WindDirection and WindDirection < 22.5 or 337.5<=WindDirection and WindDirection < 360:
                WindDirection_dir = 'S'
            if 22.5 <= WindDirection and WindDirection < 67.5:
                WindDirection_dir = 'SW'
            if 67.5 <= WindDirection and WindDirection < 112.5:
                WindDirection_dir = 'W'
            if 112.5 <= WindDirection and WindDirection < 157.5:
                WindDirection_dir = 'NW'
            if 157.5 <= WindDirection and WindDirection < 202.5:
                WindDirection_dir = 'N'
            if 202.5 <= WindDirection and WindDirection < 247.5:
                WindDirection_dir = 'NE'
            if 247.5 <= WindDirection and WindDirection < 292.5:
                WindDirection_dir = 'E'
            if 292.5 <= WindDirection and WindDirection < 337.5:
                WindDirection_dir = 'SE'
            print("WindDirection:" +str(WindDirection) +" degree","WindDirection_dir:"+WindDirection_dir)
            
            '''get wind speed'''
            # The average wind speed of the previous minute.
            try:
                WindSpeedAverage = round(0.44704 * float(databuffer[5:8]),1)
            except:
                WindSpeedAverage = 0
            print("Average Wind Speed (One Minute):" + str(WindSpeedAverage) + "m/s  ")
            # The maximum wind speed of the previous five minutes.
            try:
                WindSpeedMax = round(0.44704 * float(databuffer[9:12]),1)
            except:
                WindSpeedMax = 0     
            print("Max Wind Speed (Five Minutes):" + str(WindSpeedMax) + "m/s") 
             
            '''get temperture'''
            try:
                Temperature = round((float(databuffer[13:16]) - 32.00) * 5.00 / 9.00,2) 
            except:
                Temperature = 0
            print("Temperature:" + str(Temperature)+ "℃  ")   
            # print("Temperature:" + "{:.2f}".format(Temperature)+ "C  ")   
            
            '''get humidity'''
            try:
                Humidity = round(float(databuffer[25:27]) ,1)
            except:
                Humidity = 0
            print("Humidity:" + str(Humidity) +"%  ")
            
            '''get pressure'''
            try:
                BarPressure = round(float(databuffer[28:33])/ 10.00,1)
            except:
                BarPressure = 0
            print("BarPressure:" + str(BarPressure)  + "hPa")
            
        else: 
            databuffer = ""

    time.sleep(0.5)