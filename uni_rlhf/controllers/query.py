from flask import jsonify, send_file
from uni_rlhf.models import User, Query,QueryAnnotator,Project
from uni_rlhf.config import app, EXPORTED_PROJECT_URL
from flask import Blueprint
from uni_rlhf.utils import to_dict, datetime_converter
import csv,datetime
import json
import os
from zipfile import ZipFile

query_blueprint = Blueprint('query', __name__)


@app.route('/query/<string:project_id>', methods=['GET'])
def query(project_id):
    """
    Fetches all queries associated with a specific project.
    Args:
        - project_id (str): The project ID.
    Returns:
        - jsonify: Dictionary containing 'querys' (list of query dictionaries) and 'message'.
    Raises:
        - None: Function execution does not explicitly raise exceptions.
    """
    queries = Query.query.filter_by(project_id=project_id).all()
    queries_dicts = [to_dict(query) for query in queries]

    for query_dict in queries_dicts:
        query_annotators = QueryAnnotator.query.filter_by(query_id=query_dict['query_id']).all()
        annotator_usernames = [User.query.get(annotator.user_id).username for annotator in query_annotators]
        query_dict['annotators'] = annotator_usernames
    
    return jsonify({'querys': queries_dicts, 'message': 'success'})


@app.route('/query_annotator/<string:query_id>', methods=['GET'])
def query_annotator(query_id):
    """
    Retrieves annotators associated with a specific query.
    Args:
        - query_id (str): The query ID.
    Returns:
        - jsonify: Dictionary containing 'query_annotators' (list of annotator dictionaries) and 'message'.
    Raises:
        - None: Function execution does not explicitly raise exceptions.
    """
    query_annotators = QueryAnnotator.query.filter_by(query_id=query_id).all()
    annotators_dicts = [to_dict(annotator) for annotator in query_annotators]
    return jsonify({'query_annotators': annotators_dicts, 'message': 'success'})


@app.route('/export_label/<string:project_id>', methods=['GET'])
def export_label(project_id):
    """
    Exports label information for a specific project.
    This function generates two files: a JSON file containing the project's detailed information, and a CSV file containing detailed information of all queries in the project, along with information about annotators associated with each query.

    Args:
        - project_id (str): The unique identifier of the project to be exported.

    Returns:
        - send_file: Sends a zipped file containing the above two files as a compressed package.

    Raises:
        - 404: If the specified project is not found.
        - Other exceptions: If there are errors in creating, saving, or sending files during the process.
    """
    project = Project.query.filter_by(project_id=project_id).first()
    if not project:
        return jsonify({'message': 'Project not found'}), 404

    project_dict = to_dict(project)
    project_dict = {k: datetime_converter(v) if isinstance(v, datetime.datetime) else v for k, v in project_dict.items()}


    with open('meta_data.json', 'w') as jsonfile:
        json.dump(project_dict, jsonfile, indent=4)

    queries = Query.query.filter_by(project_id=project_id).all()

    if queries:
        with open('label.csv', 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)

            video_info_keys = set()
            label_info_keys = set()
            for query in queries:
                if query.video_info:
                    video_info_keys.update(json.loads(query.video_info).keys())
                if query.label_info:
                    label_info_keys.update(json.loads(query.label_info).keys())

            fieldnames = ['id'] + [col.name for col in queries[0].__table__.columns if col.name not in ['video_info', 'label_info','is_deleted']] + list(video_info_keys) + list(label_info_keys) + ['annotator_id', 'annotator_name']
            writer.writerow(fieldnames)

            for idx, query in enumerate(queries, 1):
                query_data = [getattr(query, col.name) for col in query.__table__.columns if col.name not in ['video_info', 'label_info','is_deleted']]
                video_info = json.loads(query.video_info) if query.video_info else {}
                label_info = json.loads(query.label_info) if query.label_info else {}

                annotator = QueryAnnotator.query.filter_by(query_id=query.query_id).first()
                annotator_id = annotator.user_id if annotator else ''
                user = User.query.filter_by(user_id=annotator_id).first()
                annotator_name = user.username if user else ''

                video_info_values = [video_info.get(key, '') for key in video_info_keys]
                label_info_values = [label_info.get(key, '') for key in label_info_keys]
                writer.writerow([idx] + query_data + video_info_values + label_info_values + [annotator_id, annotator_name])

    if not os.path.exists(EXPORTED_PROJECT_URL):
        os.makedirs(EXPORTED_PROJECT_URL)
    zip_filename = os.path.join(EXPORTED_PROJECT_URL, f'export_{project_dict["project_name"]}.zip')
    with ZipFile(zip_filename, 'w') as zipf:
        zipf.write('meta_data.json')
        zipf.write('label.csv')

    os.remove('meta_data.json')
    os.remove('label.csv')

    return send_file(zip_filename, as_attachment=True)




