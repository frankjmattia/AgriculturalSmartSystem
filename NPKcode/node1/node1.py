# -*- coding: utf-8 -*-
import time
from dfrobot_rp2040_sci import *
from pinpong.board import Board, UART
import serial 
import time
import siot
import os
from unihiker import GUI
import requests
import base64 
import cv2
#Unihiker Initialize
Board("").begin()  

# SCI Initialize
SCI1 = DFRobot_RP2040_SCI_IIC(addr=0x21)
while SCI1.begin() != 0:
    print("Initialization Sensor Universal Adapter Board failed.")
    time.sleep(1)
print("Initialization Sensor Universal Adapter Board done.")

#UART P0-RX P3-TX
uart1 = UART() 
#Initialize UART 
uart1.init(baud_rate = 9600, bits=8, parity=0, stop = 1) 

#Unihiker GUI Initialize
u_gui=GUI()
#GUI setting
soil_tem_text=u_gui.draw_text(text="soil temperature：NAN",x=0,y=0,font_size=16, color="#0000FF")
soil_hum_text=u_gui.draw_text (text="soil humidity：NAN",x=0,y=30,font_size=16, color="#0000FF")
soil_ph_text=u_gui.draw_text(text="soil ph：NAN",x=0,y=60,font_size=16, color="#0000FF")
soil_N_text=u_gui.draw_text(text="soil N：NAN",x=0,y=90,font_size=16, color="#0000FF")
soil_P_text=u_gui.draw_text(text="soil P：NAN",x=0,y=120,font_size=16, color="#0000FF")
soil_K_text=u_gui.draw_text(text="soil K：NAN",x=0,y=150,font_size=16, color="#0000FF")
CO2_text = u_gui.draw_text(text="CO2：NAN",x=0,y=180,font_size=16, color="#0000FF")
status_text = u_gui.draw_text(text="01_status：NAN",x=0,y=270,font_size=16, color="#0000FF")
air_tem_text=u_gui.draw_text(text="air temperature：NAN",x=0,y=210,font_size=16, color="#0000FF")
air_hum_text=u_gui.draw_text(text="air humidity：NAN",x=0,y=240,font_size=16, color="#0000FF")
#lux_text=u_gui.draw_text(text="light lux：NAN",x=0,y=270,font_size=16, color="#0000FF")

#command sent to soil sensor
buf = [0x02, 0x03, 0x00, 0x00, 0x00, 0x0A, 0xC5,0xFE]

#sensor default return command 
#['04', '03', '14', '00', 'e7', '00', '00', '00', '00', '00', '28', '00', '00', '00', '00', '00', '00', '00', '00', '00', '00', '25', '80', '25', 'b2']

#Calculating CRC checksum
def calc_crc(string):
    #print(string)
    #data = bytearray.fromhex(string)
    data =  ['{:02x}'.format(i) for i in string]
    #print(data)
    data = " ".join(data)
    data = data.replace('0x','')
    global data2
    data2 = data
    print(data2)
    data = bytearray.fromhex(data)
    
    crc = 0xFFFF
    for pos in data:
        crc ^= pos
        for i in range(8):
            if ((crc & 1) != 0):
                crc >>= 1
                crc ^= 0xA001
            else:
                crc >>= 1
    return hex(((crc & 0xff) << 8) + (crc >> 8))


def send_photos():
    photos_path = '/root/photos'
    photos_path_list = os.listdir(photos_path)
    photos_path_list.sort(reverse=False)
    photos_quan = len(photos_path_list)
    
    photos_count = photos_quan+1
    print("count:"+str(photos_count))
    #USB camera setting
    cap = cv2.VideoCapture(0) 
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)  
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240) 
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)     
    
    ret, frame = cap.read()
    if ret == True:
        #save photos on Unihiker
        cv2.imwrite(photos_path+'/Frame'+ str(photos_count) +'.jpg', frame)
        print("save photo!")
    cap.release()

    with open(photos_path+'/Frame'+ str(photos_count) +'.jpg',"rb") as f: 
    # b64encode是编码，b64decode是解码 
        data = base64.b64encode(f.read())
        src = "data:image/{ext};base64,{data}".format(ext='jpg', data=str(data))
        #print(src)
        #print(len(src))
        
        # Send base64 buf of the photos to the server
        siot.publish_save(topic="siot/node1/image", data=src)
        #siot.publish_save(topic="siot/image", data=src)
        print("photos send ok")
        f.close()
        status_text.config(text="04_status: photo send ok",x=0,y=290)
        photos_count = int(photos_count) + 1

count = 0
while True:
    #refresh GUI
    air_tem_value=SCI1.get_value0("Temp_Air")
    air_tem_t = "Temp_Air: "+str(air_tem_value)+"℃"
    air_tem_text.config(text=air_tem_t,x=0,y=210)
    air_hum_value=SCI1.get_value0("Humi_Air")
    air_hum__t = "Humi_Air: "+str(air_hum_value)+"%RH"
    air_hum_text.config(text=air_hum__t,x=0,y=240)

    print("-----------write buf to soil sensor-----------")
    uart1.write(buf)
    time.sleep(1)
    count=0
    #"If there is data on the serial port"
    while uart1.any()==0:
        print("any:"+str(count))
        count=count+1
        if count>10:
            break
        time.sleep(0.1)
        
    while uart1.any()>0:
        print("while2:"+str(uart1.any()))
        #print(uart1.read(uart1.any()))
        time.sleep(0.01)
        # This sensor's address is 0x02, pls review the wiki for more details.
        if uart1.read(1)[0] == 0x02:
            print("11")
            time.sleep(0.01)   
            #This sensor's default code is 0x03, pls review the wiki for more details.
            if uart1.read(1)[0] == 0x03:       
                time.sleep(0.01)  
                print("while2:"+str(uart1.any()))
                data = uart1.read(23) 
                data.insert(0,0x02)
                data.insert(1,0x03)
                #print(data)
                crc = calc_crc((data))
                #print(data[11],data(12))
                print("crc="+str(crc))
                
                if crc == '0x0':
                    print(data2)
                    data3 = data2.split()
                    #print(str(data3[10])+str(data3[11]))
                    #soil data read from soil sensor
                    soil_tem = int(str(data3[3])+str(data3[4]),16)/10
                    soil_ph = int(str(data3[9])+str(data3[10]),16)/10
                    soil_hum = int(str(data3[5])+str(data3[6]),16)/10
                    soil_N = int(str(data3[11])+str(data3[12]),16)
                    soil_P = int(str(data3[13])+str(data3[14]),16)
                    soil_K = int(str(data3[15])+str(data3[16]),16)
                    
                    #refresh GUI 
                    soil_ph_t = "soil_ph："+ str(soil_ph)
                    soil_ph_text.config(text= soil_ph_t ,x=0,y=60)
                    soil_hum_t = "soil_hum: "+str(soil_hum)+"%"
                    soil_hum_text.config(text= soil_hum_t ,x=0,y=30)
                    soil_tem_t = "soil_tem："+str(soil_tem)+"℃"
                    soil_tem_text.config(text= soil_tem_t ,x=0,y=0)
                    soil_N_t = "soil_N: "+str(soil_N)+"mg/kg"
                    soil_N_text.config(text= soil_N_t ,x=0,y=90)
                    soil_P_t = "soil_P: "+str(soil_P)+"mg/kg"
                    soil_P_text.config(text= soil_P_t ,x=0,y=120)
                    soil_K_t = "soil_K: "+str(soil_K)+"mg/kg"
                    soil_K_text.config(text= soil_K_t ,x=0,y=150)

                    try :
                        #get wifi's status
                        my_variable = requests.get("http://10.1.2.3/wifi/status")
                        print(my_variable.text)
                        status = my_variable.text.split('"')[11]
                        print("wifi: "+status)
                        status_text.config(text="01_wifi:"+status,x=0,y=270)
                        
                        #siot init and connect to the LP server. The server's IP is 10.168.1.100. 
                        #pls note that each unihiker's client_id is different. 
                        siot.init(client_id="unihiker01",server="10.168.1.100",port=1883,user="siot",password="dfrobot")
                        siot.connect()
                        siot.loop()
                        #siot subscribe the topics
                        siot.getsubscribe(topic="siot/node1/soiltemperture")
                        siot.getsubscribe(topic="siot/node1/soilhum")
                        siot.getsubscribe(topic="siot/node1/soilpH")
                        siot.getsubscribe(topic="siot/node1/soilN")
                        siot.getsubscribe(topic="siot/node1/soilP")
                        siot.getsubscribe(topic="siot/node1/soilK")
                        #siot.getsubscribe(topic="siot/node1/二氧化碳")
                        siot.getsubscribe(topic="siot/node1/airtemper")
                        siot.getsubscribe(topic="siot/node1/airhum")
                        #siot.getsubscribe(topic="siot/image")
                        siot.getsubscribe(topic="siot/node1/image")

                        siot.publish_save(topic="siot/node1/soiltemperture", data=soil_tem)
                        siot.publish_save(topic="siot/node1/soilpH", data=soil_ph)
                        siot.publish_save(topic="siot/node1/soilhum", data=soil_hum)
                        siot.publish_save(topic="siot/node1/soilN", data=soil_N)
                        siot.publish_save(topic="siot/node1/soilP", data=soil_P)
                        siot.publish_save(topic="siot/node1/soilK", data=soil_K)
                        siot.publish_save(topic="siot/node1/airtemper", data=air_tem_value)
                        siot.publish_save(topic="siot/node1/airhum", data=air_hum_value)
                        print("send ok")
                        siot.stop()
                        
                        status_text.config(text="01_status: data send ok",x=0,y=270)
                        time.sleep(3600)
                    except :        
                        print("wifi reconnect！")
                        status_text.config(text="wifi reconnect！",x=0,y=270)
                        #"ssid=dfrobot&password=dfrobot2017"  wifi ssid and wifi password
                        my_variable = requests.get("http://10.1.2.3/wifi/connect?ssid=dfrobot&password=dfrobot2017")
                        print(my_variable.text)
                        time.sleep(60)
                        my_variable = requests.get("http://10.1.2.3/wifi/status")
                        print(my_variable.text)
                        status = my_variable.text.split('"')[11]
                        print(status)
                        status_text.config(text="01_wifi:"+status,x=0,y=270)