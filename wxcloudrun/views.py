from datetime import datetime
from flask import render_template, request
from run import app
from wxcloudrun.dao import delete_counterbyid, query_counterbyid, insert_counter, update_counterbyid
from wxcloudrun.model import Counters
from wxcloudrun.response import make_succ_empty_response, make_succ_response, make_err_response
from zhipuai import ZhipuAI


@app.route('/')
def index():
    """
    :return: 返回index页面
    """
    return "Hello World!"

@app.route('/api/chat', methods=['GET'])
def chat():
    client = ZhipuAI(api_key="3cf8063a212029f13d7df043efd4a312.JXNtazBxTE2F5riK")  # 请填写您自己的APIKey
    response = client.chat.completions.create(
    model="glm-4-flash",  # 请填写您要调用的模型名称
    messages=[
        {'role': 'system', 'content': '你是一位儿童绘本的内容创意专家，你的任务是根据用户提供的主题，提供适合7岁到10岁小学生阅读的、专业的、有见地的绘本内容创意。'},
        {'role': 'user', 'content': '请以“黑神话·悟空”这款最近热门的游戏为主题，提供儿童绘本创意。要求：绘本分为4个小段，每个小段需要有插图。'},
        ],
    )
    result = response.choices[0].message
    print(result)
    return result

@app.route('/api/count', methods=['POST'])
def count():
    """
    :return:计数结果/清除结果
    """

    # 获取请求体参数
    params = request.get_json()
    print(params)
    #return params

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
