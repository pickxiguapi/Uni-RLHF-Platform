import json
import re
from flask import request
from flask import jsonify
from uni_rlhf.models import db
from uni_rlhf.config import app, db
from flask import Blueprint
import datetime
from uni_rlhf.models import db, Project, Query, QueryAnnotator

annotate_blueprint = Blueprint('annotate', __name__)


@app.route('/label_config', methods=['POST','GET'])
def label_config():
    """
    Authenticates a user and initiates a login session.
    Args:
        - None: Extracts 'project_id','user_id','query_id_list'  from request JSON.
    Returns:
        - jsonify: Dictionary containing 'instruction','question','option,url_list','feedback_type','query_length' if successful, or 'message' if failed.
    Raises:
        - None: Function execution does not explicitly raise exceptions.
    """

    project_id = request.json.get('project_id')
    user_id = request.json.get('user_id')
    query_id_list = request.json.get('query_id_list')
    project = Project.query.filter_by(project_id=project_id).first()
    instruction = project.instruction
    json_data = project.question
    feedback_type = project.feedback_type
    query_length = project.query_length
    
    url_list = []
    for i in range(len(query_id_list)):
        query = Query.query.filter_by(query_id=query_id_list[i]).first()
        url = query.video_url
        if feedback_type in ['visual', 'keypoint']:
            url = url.replace(".mp4","_img")
        url_list.append(url)
        
    # 解析 JSON 字符串为 Python 字典对象
    data = json.loads(json_data)
    # 获取字典中的键，并放入列表
    question = list(data.keys())
    # 获取字典中的值，并放入列表
    option = list(data.values())
    print(question,option)
    return jsonify({
        # 'user_id':user_id,
        # 'query_id_list':query_id_list,
        'instruction': instruction,
        'question': question,
        'options': option,
        'url':url_list,
        'feedback_type': feedback_type,
        'query_length': query_length
    })
    
    
@app.route('/save', methods=['POST','GET'])
def save():
    """
    Authenticates a user and initiates a login session.
    Args:
        - None: Extracts 'user_id','query_id','feedback_type','label' from request JSON.
    Returns:
        - jsonify: Dictionary containing 'message':'success' if successful, or 'message' if failed.
    Raises:
        - None: Function execution does not explicitly raise exceptions.
    """
    user_id = request.json.get('user_id')
    query_id = request.json.get('query_id')
    feedback_type = request.json.get('feedback_type')
    label_get = request.json.get('label')
    completion_time = datetime.datetime.now()
    #根据不同feedback设置label格式
    print("*****************")
    print(label_get)
    
    #attribute字典  label_get形式：[q1,q2,...],[op1,op2,...]  ->  {q_id:op_id,...,...}
    if feedback_type=='attribute':
        label_ = {index: value for index, value in enumerate(label_get)}
        #label_ = {q_id: op_id for q_id, op_id in zip(questions, options)}
    #comparative字典(可能不需要处理)
    elif feedback_type=='comparative':
        label_ = {index: value for index, value in enumerate(label_get)}
    #rating字典(可能不需要处理)
    elif feedback_type=='evaluative':
        label_ = {index: value for index, value in enumerate(label_get)}
    #visual字典  label_get形式：[[],[],[]]
    elif feedback_type=='visual':
        label_ = label_get
    #keypoint列表(可能不需要处理)
    elif feedback_type=='keypoint':
        label_ = label_get
    
    #插入query_annotator
    query = Query.query.filter_by(query_id=query_id).first()
    label = query.label_info
    
    #如果有人标记过，不要覆盖
    if label:
        label_info = label
        info = json.loads(label_info)
        if str(user_id) in info['label'].keys():
            info['label'][str(user_id)].update(label_)
        else:
            info['label'][str(user_id)] = label_
    
    #没人标记过，直接插入
    else:
        info = {
            "feedback_type":feedback_type,
            "label":{
                user_id:label_
            },
            "extra":None
        }
        
    json_info = json.dumps(info)
    print(info)
    query = Query.query.filter_by(query_id=query_id).first()
    marked_num = query.marked_num
    query.label_info = json_info
    query.marked_num = marked_num+1
    query.completion_time = completion_time
    db.session.commit()
    
    new_qr_an = QueryAnnotator(
        query_id=query_id,
        user_id=user_id
    )
    db.session.add(new_qr_an)
    db.session.commit()
    return jsonify({'message':'success'})



@app.route('/skip', methods=['POST','GET'])    
def skip():
    """
    Authenticates a user and initiates a login session.
    Args:
        - None: Extracts 'query_id' from request JSON.
    Returns:
        - jsonify: Dictionary containing 'message' if successful.
    Raises:
        - None: Function execution does not explicitly raise exceptions.
    """
    query_id = request.json.get('query_id')
    query = Query.query.filter_by(query_id=query_id).first()
    query.skip_num = query.skip_num+1
    db.session.commit()
    return jsonify({'message':'success'})


@app.route('/labelled_list', methods=['POST','GET'])    
def labelled_list():
    """
    Authenticates a user and initiates a login session.
    Args:
        - None: Extracts 'user_id' and 'query_id_list' from request JSON.
    Returns:
        - jsonify: Dictionary containing 'labelled_list' if successful, or 'message' if failed.
    Raises:
        - None: Function execution does not explicitly raise exceptions.
    """
    labelled = []
    user_id = request.json.get('user_id')
    query_id_list = request.json.get('query_id_list')
    for query_id in query_id_list:
        query = QueryAnnotator.query.filter_by(query_id=query_id,user_id=user_id).first()
        if query is not None:
            labelled.append(1)
        else:
            labelled.append(0)
    db.session.commit()
    return jsonify({'labelled_list': labelled})

