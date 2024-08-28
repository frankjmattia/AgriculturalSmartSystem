#  -*- coding: UTF-8 -*-

# MindPlus
# Python
import time
import siot
import os

ip = ['ping 10.168.1.114','ping 10.168.1.117','ping 10.168.1.118','ping 10.168.1.122','ping 10.168.1.115','ping 10.168.1.112']

# 事件回调函数
def on_message_callback(client, userdata, msg):
    global P1
    global N1
    global K1
    
    global P5
    global N5
    global K5
    
    global sendata1
    global sendata5
    global sendataw
    global sendata
    
    global weather_hum
    global weather_tem

    global indoor_hum
    global indoor_tem
    
    if (msg.topic.find("表格")!=-1):
        pass
    else:
        if (msg.topic.find("节点1/土壤氮")!=-1):
            N1 = msg.payload.decode()
            print(msg.topic)
            print(N1)
        if (msg.topic.find("节点1/土壤磷")!=-1):
            P1 = msg.payload.decode()
            print(msg.topic)
            print(P1)
        if (msg.topic.find("节点1/土壤钾")!=-1):
            K1 = msg.payload.decode()
            print(msg.topic)
            print(K1)
            
        status = ((not (P1 == 0)) and (not (N1 == 0)))
        
        if ((not (status == 0)) and (not (K1 == 0))):
            sendata1 = N1 +","+ P1 +","+ K1
            print(sendata1)
            siot.publish_save(topic="siot/节点1/氮磷钾总和表格", data=sendata1)


        if (msg.topic.find("节点5/土壤氮")!=-1):
            N5 = msg.payload.decode()
            print(msg.topic)
            print(N5)
        if (msg.topic.find("节点5/土壤磷")!=-1):
            P5 = msg.payload.decode()
            print(msg.topic)
            print(P5)
        if (msg.topic.find("节点5/土壤钾")!=-1):
            K5 = msg.payload.decode()
            print(msg.topic)
            print(K5)
            
        status = ((not (P5 == 0)) and (not (N5 == 0)))
        
        if ((not (status == 0)) and (not (K5 == 0))):
            sendata5 = N5 +","+ P5 +","+ K5
            print(sendata5)
            siot.publish_save(topic="siot/节点5/氮磷钾总和表格", data=sendata5)

        if (msg.topic.find("气象站/温度")!=-1):
            weather_tem = msg.payload.decode()
            print((str(msg.topic) + str(weather_tem)))
        if (msg.topic.find("气象站/湿度")!=-1):
            weather_hum = msg.payload.decode()
            print((str(msg.topic) + str(weather_hum)))

        if ((not (weather_hum == 0)) and (not (weather_tem == 0))):
            sendataw = weather_hum+ "," + weather_tem
            print(sendataw)
            siot.publish_save(topic="siot/气象站/温湿度表格", data=sendataw)
            
        if (msg.topic.find("节点1/温度")!=-1):
            weather_tem = msg.payload.decode()
            print((str(msg.topic) + str(weather_tem)))
        if (msg.topic.find("节点1/湿度")!=-1):
            weather_hum = msg.payload.decode()
            print((str(msg.topic) + str(weather_hum)))
        if ((not (indoor_hum == 0)) and (not (indoor_tem == 0))):
            sendata = indoor_hum+ "," + indoor_tem
            print(sendata)
            siot.publish_save(topic="siot/节点1/温湿度表格", data=sendata)
        

siot.init(client_id="",server="10.168.1.100",port=1883,user="siot",password="dfrobot")
siot.set_callback(on_message_callback)
siot.connect()
siot.loop()
P1 = 0
N1 = 0
K1 = 0

P5 = 0
N5 = 0
K5 = 0

weather_hum = 0
weather_tem = 0

indoor_tem = 0
indoor_hum = 0

siot.getsubscribe(topic="siot/节点1/温湿度表格")

siot.getsubscribe(topic="siot/气象站/温湿度表格")
siot.getsubscribe(topic="siot/气象站/温度")
siot.getsubscribe(topic="siot/气象站/湿度")

siot.getsubscribe(topic="siot/节点1/温度")
siot.getsubscribe(topic="siot/节点1/湿度")

siot.getsubscribe(topic="siot/devicestatus")

siot.getsubscribe(topic="siot/节点1/氮磷钾总和表格")
siot.getsubscribe(topic="siot/节点1/土壤氮")
siot.getsubscribe(topic="siot/节点1/土壤磷")
siot.getsubscribe(topic="siot/节点1/土壤钾")

siot.getsubscribe(topic="siot/节点5/氮磷钾总和表格")
siot.getsubscribe(topic="siot/节点5/土壤氮")
siot.getsubscribe(topic="siot/节点5/土壤磷")
siot.getsubscribe(topic="siot/节点5/土壤钾")

while True:
    outdev = 0
    online = 0
    for i in ip:

        result = os.popen(i)
        status = result.read()
        loc = "unreachable" in status
        print(loc)
        if loc != True:
            loc = status.find('Lost')
            loss_data = status[loc+7]
            
            if loss_data == '4':
                outdev = outdev+1
            else:
                online = online+1
        else:
            outdev = outdev+1

    output = str(online) + ','+ str(outdev)

    print("online,outdev:")
    print(output)

    siot.publish_save(topic="siot/devicestatus", data=output)
    print("send ok")
    time.sleep(100)




