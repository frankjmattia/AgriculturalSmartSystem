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
import cv2
import base64 

Board("").begin()  #初始化，选择板型，不输入板型则进行自动识别
SCI1 = DFRobot_RP2040_SCI_IIC(addr=0x21)
u_gui=GUI()
#硬串口1 P0-RX P3-TX
uart1 = UART() 
# ser = serial.Serial("/dev/ttyUSB0",115200,timeout=0.5)
#初始化串口 baud_rate 波特率, bits 数据位数(8/9) parity奇偶校验(0 无校验/1 奇校验/2 偶校验) stop 停止位(1/2)
uart1.init(baud_rate = 9600, bits=8, parity=0, stop = 1) 

soil_tem_text=u_gui.draw_text(text="soil temperature：",x=0,y=0,font_size=16, color="#0000FF")
soil_hum_text=u_gui.draw_text (text="soil humidity：",x=0,y=30,font_size=16, color="#0000FF")
soil_ph_text=u_gui.draw_text(text="soil ph：",x=0,y=60,font_size=16, color="#0000FF")
soil_N_text=u_gui.draw_text(text="soil N：",x=0,y=90,font_size=16, color="#0000FF")
soil_P_text=u_gui.draw_text(text="soil P：",x=0,y=120,font_size=16, color="#0000FF")
soil_K_text=u_gui.draw_text(text="soil K：",x=0,y=150,font_size=16, color="#0000FF")
CO2_text = u_gui.draw_text(text="CO2：",x=0,y=180,font_size=16, color="#0000FF")
status_text = u_gui.draw_text(text="02_status：NAN",x=0,y=270,font_size=16, color="#0000FF")
air_tem_text=u_gui.draw_text(text="air temperature：",x=0,y=210,font_size=16, color="#0000FF")
air_hum_text=u_gui.draw_text(text="air humidity：",x=0,y=240,font_size=16, color="#0000FF")
#lux_text=u_gui.draw_text(text="light lux：NAN",x=0,y=270,font_size=16, color="#0000FF")
while SCI1.begin() != 0:
    print("Initialization Sensor Universal Adapter Board failed.")
    time.sleep(1)
print("Initialization Sensor Universal Adapter Board done.")

#发送给传感器的指令
buf = [0x04, 0x03, 0x00, 0x00, 0x00, 0x0A, 0xC5,0x98]

#返回指令 04传感器地址,和传感器上的标签对应；03功能码；14数据长度；'00', 'e7'温度；'00', '00'湿度；00 00 空白；'00', '28'ph;'00', '00', '00', '00', '00', '00'氮磷钾；'00', '00', '00', '00'空白；'25', '80'波特率9600；25，b2校验和
#['04', '03', '14', '00', 'e7', '00', '00', '00', '00', '00', '28', '00', '00', '00', '00', '00', '00', '00', '00', '00', '00', '25', '80', '25', 'b2']
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
    cap = cv2.VideoCapture(0) 
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)  #设置摄像头图像宽度
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240) #设置摄像头图像高度
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)     #设置OpenCV内部的图像缓存，可以极大提高图像的实时性。

    ret, frame = cap.read()
    if ret == True:
        cv2.imwrite(photos_path+'/Frame'+ str(photos_count) +'.jpg', frame)
        print("save photo!")
    cap.release()

    with open(photos_path+'/Frame'+ str(photos_count) +'.jpg',"rb") as f: 
    # b64encode是编码，b64decode是解码 
        data = base64.b64encode(f.read())
        src = "data:image/{ext};base64,{data}".format(ext='jpg', data=str(data))
        #print(src)
        print(len(src))

        
        siot.publish_save(topic="siot/image", data=src)
        print("send ok")
        f.close()
        status_text.config(text="02_status: photo send ok",x=0,y=290)
        photos_count = int(photos_count) + 1



        
    
flag = 1

count=0

while True:
    CO2_value = SCI1.get_value0("CO2")
    CO2_t = "CO2: "+str(SCI1.get_value0("CO2"))+"ppm"
    CO2_text.config(text=CO2_t,x=0,y=180)
    air_tem_value=SCI1.get_value0("Temp_Air")
    air_tem_t = "Temp_Air: "+str(air_tem_value)+"℃"
    air_tem_text.config(text=air_tem_t,x=0,y=210)
    air_hum_value=SCI1.get_value0("Humi_Air")
    air_hum__t = "Humi_Air: "+str(air_hum_value)+"%RH"
    air_hum_text.config(text=air_hum__t,x=0,y=240)

    print("-----------write buf-----------")
    uart1.write(buf)
    time.sleep(1)
    count=0
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
        if uart1.read(1)[0] == 0x04:
            print("11")
            time.sleep(0.01)   
            if uart1.read(1)[0] == 0x03:       
                time.sleep(0.01)  
                print("while2:"+str(uart1.any()))
                data = uart1.read(23) 
                data.insert(0,0x04)
                data.insert(1,0x03)
                #print(data)
                crc = calc_crc((data))
                #print(data[11],data(12))
                print("crc="+str(crc))
                
                if crc == '0x0':
                    print(data2)
                    data3 = data2.split()
                    #print(str(data3[10])+str(data3[11]))

                    soil_tem = int(str(data3[3])+str(data3[4]),16)/10
                    soil_ph = int(str(data3[9])+str(data3[10]),16)/10
                    soil_hum = int(str(data3[5])+str(data3[6]),16)/10
                    soil_N = int(str(data3[11])+str(data3[12]),16)
                    soil_P = int(str(data3[13])+str(data3[14]),16)
                    soil_K = int(str(data3[15])+str(data3[16]),16)

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
                        my_variable = requests.get("http://10.1.2.3/wifi/status")
                        print(my_variable.text)
                        status = my_variable.text.split('"')[11]
                        print("wifi: "+status)

                        status_text.config(text="02_wifi:"+status,x=0,y=270)

                        siot.init(client_id="unihiker02",server="10.168.1.100",port=1883,user="siot",password="dfrobot")
                        siot.connect()
                        siot.loop()

                        siot.getsubscribe(topic="siot/image")
                        siot.getsubscribe(topic="siot/节点2/土壤温度")
                        siot.getsubscribe(topic="siot/节点2/土壤湿度")
                        siot.getsubscribe(topic="siot/节点2/土壤pH")
                        siot.getsubscribe(topic="siot/节点2/土壤氮")
                        siot.getsubscribe(topic="siot/节点2/土壤磷")
                        siot.getsubscribe(topic="siot/节点2/土壤钾")
                        siot.getsubscribe(topic="siot/节点2/二氧化碳")
                        siot.getsubscribe(topic="siot/节点2/空气温度")
                        siot.getsubscribe(topic="siot/节点2/空气湿度")

                        siot.publish_save(topic="siot/节点2/土壤温度", data=soil_tem)
                        siot.publish_save(topic="siot/节点2/土壤pH", data=soil_ph)
                        siot.publish_save(topic="siot/节点2/土壤湿度", data=soil_hum)
                        siot.publish_save(topic="siot/节点2/土壤氮", data=soil_N)
                        siot.publish_save(topic="siot/节点2/土壤磷", data=soil_P)
                        siot.publish_save(topic="siot/节点2/土壤钾", data=soil_K)
                        siot.publish_save(topic="siot/节点2/二氧化碳", data=CO2_value)
                        siot.publish_save(topic="siot/节点2/空气温度", data=air_tem_value)
                        siot.publish_save(topic="siot/节点2/空气湿度", data=air_hum_value)
                        

                        
                        if flag == 10:
                            flag = 0
                            send_photos()
                        '''
                        siot.getsubscribe(topic="siot/u02_soil_ph")
                        siot.getsubscribe(topic="siot/u02_soil_hum")
                        siot.getsubscribe(topic="siot/u02_soil_N")
                        siot.getsubscribe(topic="siot/u02_soil_P")
                        siot.getsubscribe(topic="siot/u02_soil_K")
                        siot.getsubscribe(topic="siot/u02_CO2_value")
                        siot.getsubscribe(topic="siot/u02_air_tem")
                        siot.getsubscribe(topic="siot/u02_air_hum")
                        
                        siot.publish_save(topic="siot/u02_soil_tem", data=soil_tem)
                        
                        siot.publish_save(topic="siot/u02_soil_ph", data=soil_ph)
                        siot.publish_save(topic="siot/u02_soil_hum", data=soil_hum)
                        siot.publish_save(topic="siot/u02_soil_N", data=soil_N)
                        siot.publish_save(topic="siot/u02_soil_P", data=soil_P)
                        siot.publish_save(topic="siot/u02_soil_K", data=soil_K)
                        siot.publish_save(topic="siot/u02_CO2_value", data=CO2_value)
                        siot.publish_save(topic="siot/u02_air_tem", data=air_tem)
                        siot.publish_save(topic="siot/u02_air_hum", data=air_hum)
                        '''
                        print("send ok")
                        siot.stop()
                        status_text.config(text="02_status: data send ok",x=0,y=270)
                        time.sleep(10)
                    except :        
                        print("wifi正在重连！")
                        status_text.config(text="02_wifi正在重连！",x=0,y=270)
                        my_variable = requests.get("http://10.1.2.3/wifi/connect?ssid=dfrobot&password=dfrobot2017") # ssid和password后面改为需要连接的wifi名字密码
                        print(my_variable.text)
                        time.sleep(60)
                        print("查看WiFi连接情况：")
                        my_variable = requests.get("http://10.1.2.3/wifi/status")
                        print(my_variable.text)
                        status = my_variable.text.split('"')[11]
                        print(status)
                        status_text.config(text="02_wifi:"+status,x=0,y=270)
                        
    
     
                    
