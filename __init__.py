import sys
import os
from time import sleep

from flask import Flask, request, jsonify, render_template

import json

from .Algo import Algo

app = Flask(__name__)
global algo
algo = Algo()


@app.route('/')
def index():
      return render_template('page.html')

@app.route('/restart-algo',methods=['GET'])
def restart():
    global algo #global algo in order to refer to the global var and not a local one
    del algo
    algo = Algo()
    return ""

@app.route('/print1_5',methods=['GET'])
def print1_5():
    algo.print1_5()
    return ""


@app.route('/print6_10',methods=['GET'])
def print6_10():
    algo.print6_10()
    return ""


@app.route('/send-yes-or-no',methods=['POST'])
def getYESorNO():
    data = request.data.decode('utf-8')

    res = json.loads(data)['res']
    print("server: call to algo.respon with:"+str(res))
    ans = algo.respon(res)
    return jsonify(
        areWeFinish=ans,
        numOfRelevantDishes=algo.getNumOfRelevantDishes()
        ) # return json

@app.route('/get-next-att',methods=['GET'])
def sendAtt():
    print("The server send: "+str(algo.getNextAtt()))
    print(algo.getNumOfRelevantDishes())
    return jsonify(
        nextAtt=algo.getNextAtt(),
        numOfRelevantDishes=algo.getNumOfRelevantDishes(),
        nextAttImage=algo.getAttImage()
        ) # return json

@app.route('/get-rec-urls',methods=['GET'])
def getRecUrls():
    return jsonify(
        recipesUrls=algo.getRecipesUrls()
    )

@app.route('/get-preview-info',methods=['GET'])
def getPreviewInfo():
    return jsonify(
        recPreviewInfo=algo.getPreviewInfo()
    )

if __name__ == '__main__':

    app.run(host='127.0.0.1',port='80')
    # app.run(host='10.200.203.231',port=5005)