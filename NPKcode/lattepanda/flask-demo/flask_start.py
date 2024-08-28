#  -*- coding: UTF-8 -*-

# MindPlus
# Python
from flask import Flask,Response,render_template,request
flask_app = Flask(__name__)

# 事件回调函数
def rec_route_funca():
    print("b click")
    return "rount_func"
def rec_route_funcb():
    print("b click")
    return "b"
def rec_index():
    return render_template("test.html")


@flask_app.route('/index',methods=['GET','POST'])
def route_index():
    return rec_index()
flask_app.run(host='0.0.0.0', port=5000, threaded=True)
