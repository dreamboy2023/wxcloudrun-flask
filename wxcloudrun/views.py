from datetime import datetime
from flask import render_template, request, Response
from run import app
from wxcloudrun.dao import delete_counterbyid, query_counterbyid, insert_counter, update_counterbyid
from wxcloudrun.model import Counters
from wxcloudrun.response import make_succ_empty_response, make_succ_response, make_err_response
import requests


@app.route('/')
def index():
    return "hello world"

def callDeepSeek(messages, key):
    # 定义请求URL和头信息
    url = 'https://api.deepseek.com/chat/completions'
    headers = {
        'Authorization': f"Bearer {key}",
        'Content-Type': 'application/json'
    }
    tools = [
        {
            "type": "function",
            "function": {
                "name": "get_time",
                "description": "获取当前时间",
                "parameters": {
                    "type": "object",
                    "properties": {
                    }
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "baidu_search",
                "description": "通过百度搜索引擎获取信息, 用户需要输入搜索关键词",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "query, 比如北京在哪里、丁磊",
                        }
                    },
                    "required": ["query"]
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_weather",
                "description": "获取某个地点的天气情况，需要用户输入地点",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "城市或地区, 比如天津、宁波",
                        }
                    },
                    "required": ["location"]   
                }
            }
        }
    ]

    requestData = {
      "model": "deepseek-chat",
      "messages": messages,
      "stream": True,
      "tools": tools
    }
    return requests.post(url, headers=headers, json=requestData, stream=True).json()["choices"][0]["message"]
    # # 输出结果
    # response_data = response.json()
    # result = response_data["choices"][0]["message"]
    # return result

@app.route('/api/chat', methods=['POST'])
def chat():
    # 获取请求体参数
    params = request.get_json()
    print(params)
    messages = params['messages']
    key = params['key']
    result = callDeepSeek(messages, key)
    return result

@app.route('/api/chatstream', methods=['POST'])
def chat():
    # 获取请求体参数
    params = request.get_json()
    print(params)
    messages = params['messages']
    key = params['key']
    return Response(callDeepSeek(messages, key), content_type='text/event-stream')

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
