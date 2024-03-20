import pytest
from flask import json
from uni_rlhf.models import db, Query, QueryAnnotator, User
from uni_rlhf.config import app as flask_app

@pytest.fixture
def app():
    app = flask_app
    app.config.update({
        "TESTING": True,
    })
    with app.app_context():
        db.create_all()
    yield app
    with app.app_context():
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

def test_query(client):
    # Setup test data
    project_id = "testproject"
    query1 = Query(query_id="query1", project_id=project_id)
    query2 = Query(query_id="query2", project_id=project_id)
    db.session.add_all([query1, query2])
    db.session.commit()

    response = client.get(f"/query/{project_id}")
    assert response.status_code == 200
    data = json.loads(response.data)
    assert "querys" in data
    assert len(data["querys"]) == 2

def test_query_annotator(client):
    user = User(username="testuser", password="testpassword")
    query = Query(query_id="query1", project_id="testproject")
    annotator = QueryAnnotator(query_id="query1", user_id=user.user_id)
    db.session.add_all([user, query, annotator])
    db.session.commit()

    response = client.get(f"/query_annotator/{query.query_id}")
    assert response.status_code == 200
    data = json.loads(response.data)
    assert "query_annotators" in data
    assert len(data["query_annotators"]) == 1
