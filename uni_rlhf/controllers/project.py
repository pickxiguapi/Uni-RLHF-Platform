from flask import Blueprint
from flask import request
from flask import jsonify
import datetime
from datetime import datetime
import os
import shortuuid
import json
from uni_rlhf.models import db, User, Project, Query,UserProject
from uni_rlhf.config import app, db, celery, BASE_URL, UPLOAD_DATASETS_URL
from uni_rlhf.utils import to_dict, allowed_file
from flask import jsonify
from jsonschema import validate, ValidationError
import h5py
from werkzeug.utils import secure_filename


project_blueprint = Blueprint('project', __name__)


@app.route('/projects/<string:username>', methods=['POST'])
def projects(username):
    """
    Fetches all projects and the current projects associated with a specific user.
    Args:
        - username (str): The username.
    Returns:
        - jsonify: Dictionary containing 'projects' and 'currentprojects', each a list of project dictionaries.
    Raises:
        - 404: If the user is not found.
    """
    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({'message': 'User not found'}), 404

    user_id = user.user_id
    projects = Project.query.filter_by(is_deleted=0).all()
    userprojects = UserProject.query.filter_by(user_id=user_id).all()

    projects_list = []
    current_projects_list = []

    for project in projects:
        if project.visibility:
            associated_usernames = [u.username for u in User.query.join(UserProject, User.user_id == UserProject.user_id).filter(UserProject.project_id == project.project_id)]
            skip_num = db.session.query(db.func.sum(Query.skip_num)).filter(Query.project_id == project.project_id).scalar() or 0

            project_dict = to_dict(project)
            project_dict.update({"associated_usernames": associated_usernames, "skip_num": skip_num})

            projects_list.append(project_dict)
        if any(up.project_id == project.project_id for up in userprojects):
            current_projects_list.append(project_dict)

    return jsonify({'projects': projects_list, 'currentprojects': current_projects_list})


@app.route('/create_new_project/<string:username>', methods=['POST'])
def create_new_project(username):
    """
    Creates a new project.
    Args:
        - username (str): The username of the user creating the project.
    Returns:
        - jsonify: Dictionary with 'username', 'projects', and 'message'.
    Raises:
        - 404: If the user is not found.
    """
    try:
        data = request.json
    except ValidationError as e:
        return jsonify({'error': 'Invalid data', 'message': str(e)}), 400
    
    project_id = str(shortuuid.uuid())
    project_name = data.get('project_name')
    description = data.get('description')
    visibility = data.get('visibility')
    dataset_path = data.get('dataset_path')
    domain = data.get('domain')
    task = data.get('task')
    environment_name = data.get('environment_name')
    instruction = data.get('instruction')
    mode = data.get('mode')
    sampler_type = data.get('sampler_type')
    feedback_type = data.get('feedback_type')
    question = json.dumps(data.get('question'))
    query_num = data.get('query_num')
    query_length = data.get('query_length')
    video_width = data.get('video_width')
    video_height = data.get('video_height')
    fps = data.get('fps')
    create_time = datetime.now()
    due_time = data.get('due_time')
    status = 'creation'
    annotation_num = 0  
    is_deleted = 0  # default

    user = User.query.filter_by(username=username).first()
    
    # TODO TODO TODO
    # Boundary hard coding
    if task == "adroit":
        if "pen" in environment_name:
            query_length = min(int(query_length), 60)
        else:
            query_length = min(int(query_length), 80)
    elif task == "minigrid":
        query_length = min(int(query_length), 10)
    else:
        pass
    
    if domain == "vd4rl":
        query_length = min(int(query_length), 500)
    elif domain == 'smarts':
        query_length = min(int(query_length), 50) 
    else:
        pass
    
    new_project = Project(
        project_id=project_id,
        project_name=project_name,
        description=description,
        due_time=due_time,
        visibility=visibility,
        dataset_path=dataset_path,
        domain=domain,
        task=task,
        environment_name=environment_name,
        instruction=instruction,
        mode=mode,
        sampler_type=sampler_type,
        feedback_type=feedback_type,
        query_num=query_num,
        query_length=query_length,
        video_width=video_width,
        video_height=video_height,
        fps=fps,
        creator=user.user_id,
        create_time=create_time,
        status=status,
        annotation_num=annotation_num,
        question=question,
        is_deleted=is_deleted
    )
    db.session.add(new_project)

    new_user_project = UserProject(user_id=user.user_id, project_id=project_id, is_deleted=is_deleted)
    db.session.add(new_user_project)
    db.session.commit()
    
    bind_project(project_id,username)
    
    projects = Project.query.all()
    projects = [to_dict(project) for project in projects]
    
    save_dir = f"{BASE_URL}{project_id}_{environment_name}_{mode}_{feedback_type}"

    new_project=to_dict(new_project)
    new_project.update({"save_dir": save_dir})
    if not os.path.exists(new_project['save_dir']):
        os.makedirs(new_project['save_dir'])
    
    try:
        generate_video.delay(new_project, project_id)            
    except Exception as e:
        print(f"Error during create: {e}")
    
    return jsonify({'username':username, 'projects':projects, 'message':'create success'})


@celery.task(name='__main__.generate_video')
def generate_video(cfg, project_id):
    context = {}
    exec(f"from uni_rlhf.datasets import {cfg['mode']}_{cfg['domain'].lower()} as dataset_module", context)
    datasets = context['dataset_module']
    with app.app_context():
        dataset = datasets.Dataset(project_id=cfg['project_id'], domain=cfg['domain'], task=cfg['task'], 
                                environment_name=cfg['environment_name'], mode=cfg['mode'],
                                sampler_type=cfg['sampler_type'], feedback_type=cfg['feedback_type'], 
                                query_num=cfg['query_num'], query_length=cfg['query_length'], 
                                fps=cfg['fps'], video_width=cfg['video_width'], video_height=cfg['video_height'],
                                save_dir=cfg['save_dir'])
        video_info_list, video_url_list, query_id_list = dataset.generate_video_resources()
        # if cfg['dataset_path'] is None or "":
        #     video_info_list, video_url_list, query_id_list = dataset.generate_video_resources()
        # else : 
        #     dataset.generate_video_resources(cfg['dataset_path'])

        if not video_info_list or not video_url_list or not query_id_list:
            raise ValueError("generate_video_resources did not return expected data")
        
        for i in range(len(query_id_list)):
            query_id = query_id_list[i]
            video_url = video_url_list[i].replace("./uni_rlhf/vue_part/src","@")
            video_info_json = json.dumps(video_info_list[i])

            try:
                new_query = create_new_query(query_id, project_id, video_url, video_info_json)
                db.session.add(new_query)
                db.session.commit()
                print("insert successfully")
            except Exception as e:
                print(f"Error during insert: {e}")
                db.session.rollback()

        try:
            update_project_status(project_id, "activation")
        except Exception as e:
            print(f"Error updating project status: {e}")
            

def create_new_query(query_id, project_id, url, video_info_json):
    return Query(
        query_id=query_id,
        project_id=project_id,
        marked_num=0,
        skip_num=0,
        video_info=video_info_json,
        video_url=url
    )


def update_project_status(project_id, new_status):
    project = Project.query.get(project_id)
    if project:
        project.status = new_status
        db.session.commit()
        print("Status updated")

    
@app.route('/project_status/<string:project_id>', methods=['POST'])
def project_status(project_id):
    """
    Retrieves the current status of a specified project.
    Args:
        - project_id (str): The project ID.
    Returns:
        - jsonify: Dictionary containing 'status' and 'message'.
    Raises:
        - None: Returns a project not found message if the project does not exist.
    """
    project = Project.query.filter_by(project_id=project_id).first()
    if project:
        return jsonify({'status': project.status, 'message': 'success'})
    else:
        return jsonify({'message': 'Project not found'})

    
@app.route('/project/<string:project_id>/<string:username>')
def project_page(project_id, username):
    """
    Retrieves detailed information of a specified project.
    Args:
        - project_id (str): The project ID.
        - username (str): The username.
    Returns:
        - jsonify: Dictionary with 'username', 'user_id', 'project' (detailed project dictionary), and 'deletable'.
    Raises:
        - 404: If the project or user is not found.
    """
    project = Project.query.filter_by(project_id=project_id).first()
    user = User.query.filter_by(username=username).first()

    if not project or not user:
        return jsonify({'message': 'Project or user not found'}), 404

    project_dict = to_dict(project)

    associated_users = User.query.join(UserProject, User.user_id == UserProject.user_id).filter(UserProject.project_id == project_id)
    project_dict['associated_usernames'] = [user.username for user in associated_users]

    deletable = '1' if user.user_id == project.creator else '0'
    
    annotations = db.session.query(db.func.sum(Query.marked_num)).filter(Query.project_id == project_id).scalar() or 0
    deletable = '1' if user.user_id == project.creator else '0'
    project_dict['annotations'] = annotations  
    return jsonify({'username': username, 'user_id': user.user_id, 'project': project_dict, 'deletable': deletable})


# delete
@app.route('/delete_project/<string:project_id>/<string:username>', methods=['GET'])
def delete_project(project_id, username):
    """
    Deletes a specified project.
    Args:
        - project_id (str): The project ID.
        - username (str): The username.
    Returns:
        - jsonify: Dictionary with 'username', 'projects' (updated list of project dictionaries), and 'message'.
    Raises:
        - 404: If the project is not found.
    """
    project = Project.query.filter_by(project_id=project_id).first()
    if not project:
        return jsonify({'username': username, 'message': 'No project found'}), 404

    UserProject.query.filter_by(project_id=project_id).delete()
    QueryAnnotator.query.filter_by(project_id=project_id).delete()
    Query.query.filter_by(project_id=project_id).delete()

    db.session.delete(project)
    db.session.commit()

    projects = Project.query.all()
    projects_dicts = [to_dict(project) for project in projects]

    return jsonify({'username': username, 'projects': projects_dicts, 'message': 'Delete success'})


# bind project
@app.route('/bind_project/<string:project_id>/<string:username>', methods=['GET'])
def bind_project(project_id, username):
    """
    Binds a user to a specified project.
    Args:
        - project_id (str): The project ID.
        - username (str): The username.
    Returns:
        - jsonify: Dictionary with 'username', 'project_id', and 'message'.
    Raises:
        - 404: If the user is not found.
        - 409: If the project is already bound to the user.
    """
    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({'error': 'User not found', 'username': username}), 404

    existing_bind = UserProject.query.filter_by(user_id=user.user_id, project_id=project_id).first()
    if existing_bind:
        return jsonify({'error': 'Project already bound to user', 'username': username, 'project_id': project_id}), 409

    new_bind = UserProject(user_id=user.user_id, project_id=project_id)
    db.session.add(new_bind)
    db.session.commit()
    return jsonify({'username': username, 'project_id': project_id, 'message': 'bind success'})


@app.route('/project_user/<string:project_id>', methods=['GET'])
def project_user(project_id):
    """
    Retrieves all users associated with a specific project.
    Args:
        - project_id (str): The project ID.
    Returns:
        - jsonify: Dictionary containing 'project_users' (list of user-project association dictionaries) and 'message'.
    Raises:
        - None: Returns an empty list if the project does not exist.
    """
    project_users = UserProject.query.filter_by(project_id=project_id).all()
    project_users_dicts = [to_dict(user_project) for user_project in project_users]
    return jsonify({'project_users': project_users_dicts, 'message': 'success'})


@app.route('/get_default_json')
def get_default_json():
    with open('uni_rlhf/dataset_validator/default_configuration.json', 'r') as file:
        data = json.load(file)
        return jsonify(data)


@app.route('/upload_hdf5', methods=['POST'])
def upload_hdf5():
    """
    Handles the uploading and processing of HDF5 files.
    Args:
        - None: Extracts the file from the request files.
    Returns:
        - jsonify: Dictionary containing either a 'message' indicating success or an 'error' message.
    Raises:
        - None: Function execution does not explicitly raise exceptions.
    """
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'})

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No selected file'})

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(UPLOAD_DATASETS_URL, filename)
        try:
            file.save(file_path)
            return jsonify({'message': 'File uploaded successfully', 'file_path': file_path})
        except Exception as e:
            return jsonify({'error': f'Error saving file: {str(e)}'})
    else:
        return jsonify({'error': 'Invalid file format. Please upload an HDF5 file'})


