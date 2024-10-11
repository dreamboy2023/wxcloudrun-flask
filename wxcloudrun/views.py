from datetime import datetime
from flask import render_template, request
from run import app
from wxcloudrun.dao import delete_counterbyid, query_counterbyid, insert_counter, update_counterbyid
from wxcloudrun.model import Counters
from wxcloudrun.response import make_succ_empty_response, make_succ_response, make_err_response
import requests


@app.route('/')
def index():
    
    return "hello world"

@app.route('/api/chat', methods=['POST'])
def chat():
    # 定义请求URL和头信息
    url = 'https://api.deepseek.com/chat/completions'
    headers = {
        'Authorization': 'Bearer ',
        'Content-Type': 'application/json'
    }
    # 获取请求体参数
    params = request.get_json()
    systemprompt = params['systemprompt']
    round1 = params['round1']
    data = {
        "model": "deepseek-chat",
        "messages":[
            {
                "role": "system", 
                "content": systemprompt
            },
            {
                "role": "user", 
                "content": round1
            }
        ]
    }
    response = requests.post(url, headers=headers, json=data)

    # 输出结果
    response_data = response.json()
    result = response_data["choices"][0]["message"]
    return result

@app.route('/api/count', methods=['POST'])
def count():
    """
    :return:计数结果/清除结果
    """

    # 获取请求体参数
    params = request.get_json()

    # 检查action参数
    if 'action' not in params:
        return make_err_response('缺少action参数')

    # 按照不同的action的值，进行不同的操作
    action = params['action']

    # 执行自增操作
    if action == 'inc':
        counter = query_counterbyid(1)
        if counter is None:
            counter = Counters()
            counter.id = 1
            counter.count = 1
            counter.created_at = datetime.now()
            counter.updated_at = datetime.now()
            insert_counter(counter)
        else:
            counter.id = 1
            counter.count += 1
            counter.updated_at = datetime.now()
            update_counterbyid(counter)
        return make_succ_response(counter.count)

    # 执行清0操作
    elif action == 'clear':
        delete_counterbyid(1)
        return make_succ_empty_response()

    # action参数错误
    else:
        return make_err_response('action参数错误')


@app.route('/api/count', methods=['GET'])
def get_count():
    """
    :return: 计数的值
    """
    counter = Counters.query.filter(Counters.id == 1).first()
    return make_succ_response(0) if counter is None else make_succ_response(counter.count)
