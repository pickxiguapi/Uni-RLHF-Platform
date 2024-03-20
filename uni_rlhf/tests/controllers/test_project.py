import pytest
from flask import json
from uni_rlhf.models import db, User, Project, UserProject
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

@pytest.fixture
def runner(app):
    return app.test_cli_runner()

def test_fetch_projects(client):
    user = User(username="testuser", password="testpassword", email="test@example.com")
    project = Project(project_id="testproject", project_name="Test Project")
    db.session.add_all([user, project])
    db.session.commit()
    
    response = client.get("/projects/testuser")
    assert response.status_code == 200
    data = json.loads(response.data)
    assert "projects" in data
    assert "currentprojects" in data

def test_createnewproject(client):
    response = client.post("/createnewproject/testuser", json={
        "project_name": "New Project",
    })
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["message"] == "create success"

def test_delete_project(client):
    response = client.get("/delete_project/testproject/testuser")
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["message"] == "Delete success"

def test_bind_project(client):
    response = client.get("/bind_project/testproject/testuser")
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["message"] == "bind success"

