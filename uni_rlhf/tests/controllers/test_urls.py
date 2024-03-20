import pytest
from flask import json

@pytest.mark.usefixtures("testapp")
class TestURLs:
    def test_fetch_projects(self, testapp):
        response = testapp.get('/projects/testuser')
        assert response.status_code == 200

    def test_create_new_project(self, testapp):
        project_data = {...}  
        response = testapp.post('/createnewproject/testuser', json=project_data)
        assert response.status_code == 200

    def test_project_status(self, testapp):
        response = testapp.post('/project_status/test_project_id')
        assert response.status_code == 200

    def test_project_page(self, testapp):
        response = testapp.get('/project/test_project_id/testuser')
        assert response.status_code == 200

    def test_delete_project(self, testapp):
        response = testapp.get('/delete_project/test_project_id/testuser')
        assert response.status_code == 200 or response.status_code == 404

    def test_bind_project(self, testapp):
        response = testapp.get('/bind_project/test_project_id/testuser')
        assert response.status_code == 200 or response.status_code == 409

    def test_project_user(self, testapp):
        response = testapp.get('/project_user/test_project_id')
        assert response.status_code == 200

    def test_query(self, testapp):
        response = testapp.get('/query/test_project_id')
        assert response.status_code == 200

    def test_query_annotator(self, testapp):
        response = testapp.get('/query_annotator/test_query_id')
        assert response.status_code == 200


