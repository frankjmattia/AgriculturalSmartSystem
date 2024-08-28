# -*- coding: utf-8 -*-
#节点4主代码。要求：行空板siot版本1.0.3，server ip需要和siot服务器（LP）的ip一致，行空板和LP在一个局域网
#siot服务器的topic必须提前创建
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

Board("").begin()  #初始化，选择板型，不输入板型则进行自动识别
SCI1 = DFRobot_RP2040_SCI_IIC(addr=0x21)
u_gui=GUI()
#硬串口1 P0-RX P3-TX
uart1 = UART() 
# ser = serial.Serial("/dev/ttyUSB0",115200,timeout=0.5)
#初始化串口 baud_rate 波特率, bits 数据位数(8/9) parity奇偶校验(0 无校验/1 奇校验/2 偶校验) stop 停止位(1/2)
uart1.init(baud_rate = 9600, bits=8, parity=0, stop = 1) 

soil_tem_text=u_gui.draw_text(text="soil temperature：NAN",x=0,y=0,font_size=16, color="#0000FF")
soil_hum_text=u_gui.draw_text (text="soil humidity：NAN",x=0,y=30,font_size=16, color="#0000FF")
soil_ph_text=u_gui.draw_text(text="soil ph：NAN",x=0,y=60,font_size=16, color="#0000FF")
soil_N_text=u_gui.draw_text(text="soil N：NAN",x=0,y=90,font_size=16, color="#0000FF")
soil_P_text=u_gui.draw_text(text="soil P：NAN",x=0,y=120,font_size=16, color="#0000FF")
soil_K_text=u_gui.draw_text(text="soil K：NAN",x=0,y=150,font_size=16, color="#0000FF")
CO2_text = u_gui.draw_text(text="CO2：NAN",x=0,y=180,font_size=16, color="#0000FF")
status_text = u_gui.draw_text(text="status：NAN",x=0,y=290,font_size=16, color="#0000FF")
air_tem_text=u_gui.draw_text(text="air temperature：NAN",x=0,y=210,font_size=16, color="#0000FF")
air_hum_text=u_gui.draw_text(text="air humidity：NAN",x=0,y=240,font_size=16, color="#0000FF")
lux_text=u_gui.draw_text(text="light lux：NAN",x=0,y=270,font_size=16, color="#0000FF")

while SCI1.begin() != 0:
    print("Initialization Sensor Universal Adapter Board failed.")
    time.sleep(1)
print("Initialization Sensor Universal Adapter Board done.")

#发送给传感器的指令
buf = [0x05, 0x03, 0x00, 0x00, 0x00, 0x0A, 0xC4,0x49]

#返回指令 04传感器地址；03功能码；14数据长度；'00', 'e7'温度；'00', '00'湿度；00 00 空白；'00', '28'ph;'00', '00', '00', '00', '00', '00'氮磷钾；'00', '00', '00', '00'空白；'25', '80'波特率9600；25，b2校验和
#['04', '03', '14', '00', 'e7', '00', '00', '00', '00', '00', '28', '00', '00', '00', '00', '00', '00', '00', '00', '00', '00', '25', '80', '25', 'b2']
def calc_crc(string):
    
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
        siot.publish_save(topic="siot/节点4/image", data=src)
        print("photos send ok")
        f.close()
        photos_count = int(photos_count) + 1



        
    
flag = 1
while True:
    print("aaa")
    light_value = SCI1.get_value0("Light")
    light_t = "light: "+str(light_value)+" lx"
    lux_text.config(text=light_t,x=0,y=270)

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
        if uart1.read(1)[0] == 0x05:
            print("11")
            time.sleep(0.01)   
            if uart1.read(1)[0] == 0x03:       
                time.sleep(0.01)  
                print("while2:"+str(uart1.any()))
                data = uart1.read(23) 
                data.insert(0,0x05)
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

                        status_text.config(text="wifi:"+status,x=0,y=290)

                        siot.init(client_id="unihiker04",server="10.168.1.100",port=1883,user="siot",password="dfrobot")
                        siot.connect()
                        siot.loop()


                        siot.getsubscribe(topic="siot/节点4/土壤温度")
                        siot.getsubscribe(topic="siot/节点4/土壤湿度")
                        siot.getsubscribe(topic="siot/节点4/土壤pH")
                        siot.getsubscribe(topic="siot/节点4/土壤氮")
                        siot.getsubscribe(topic="siot/节点4/土壤磷")
                        siot.getsubscribe(topic="siot/节点4/土壤钾")
                        siot.getsubscribe(topic="siot/节点4/光照强度")
                        siot.getsubscribe(topic="siot/image")
                        siot.getsubscribe(topic="siot/节点4/image")
                        
                        siot.publish_save(topic="siot/节点4/光照强度", data=SCI1.get_value0("Light"))
                        siot.publish_save(topic="siot/节点4/土壤温度", data=soil_tem)
                        siot.publish_save(topic="siot/节点4/土壤pH", data=soil_ph)
                        siot.publish_save(topic="siot/节点4/土壤湿度", data=soil_hum)
                        siot.publish_save(topic="siot/节点4/土壤氮", data=soil_N)
                        siot.publish_save(topic="siot/节点4/土壤磷", data=soil_P)
                        siot.publish_save(topic="siot/节点4/土壤钾", data=soil_K)
                        siot.publish_save(topic="siot/节点4/光照强度", data=SCI1.get_value0("Light"))
                        send_photos()
                        
                        if flag == 50:
                            flag = 0
                            send_photos()
                        


                        print("data send ok")
                        siot.stop()
                        status_text.config(text="status: data send ok",x=0,y=290)
                        print("flag:")
                        print(flag)
                        flag = flag + 1
                        time.sleep(3600)
                    
                    except :        
                        print("正在重连服务器！")
                        status_text.config(text="正在重连服务器！",x=0,y=290)
                        my_variable = requests.get("http://10.1.2.3/wifi/connect?ssid=dfrobot&password=dfrobot2017") # ssid和password后面改为需要连接的wifi名字密码
                        print(my_variable.text)
                        time.sleep(60)
                        print("查看WiFi连接情况：")
                        my_variable = requests.get("http://10.1.2.3/wifi/status")
                        print(my_variable.text)
                        status = my_variable.text.split('"')[11]
                        print(status)
                        status_text.config(text="wifi:"+status,x=0,y=290)
                    


                        
    
     
                    
