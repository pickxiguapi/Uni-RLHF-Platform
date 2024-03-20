import pytest,datetime
from uni_rlhf.models import db, User, Project, Query, UserProject, QueryAnnotator
from uni_rlhf.config import create_app

@pytest.fixture(scope='module')
def test_app():
    app = create_app()
    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"
    })

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture(scope='module')
def test_client(test_app):
    return test_app.test_client()

def test_user_model(test_app):
    with test_app.app_context():
        user = User(username='testuser', password='testpass', email='test@test.com')
        db.session.add(user)
        db.session.commit()
        assert User.query.count() == 1
        assert User.query.first().username == 'testuser'

def test_project_model(test_app):
    with test_app.app_context():
        project = Project(project_id='123', project_name='Test Project', description='Test description', due_time=datetime.utcnow(), visibility=1, dataset_path='path/to/dataset', domain='test_domain', task='test_task', environment_name='test_environment', instruction='test_instruction', mode='test_mode', sampler_type='random', feedback_type='visual', query_num=10, query_length=200, video_width=1920, video_height=1080, fps=30, creator=1, create_time=datetime.utcnow(), status='active', annotation_num=0, question='test_question', options='test_options')
        db.session.add(project)
        db.session.commit()
        assert Project.query.count() == 1
        assert Project.query.first().project_name == 'Test Project'

def test_query_model(test_app):
    with test_app.app_context():
        query = Query(query_id='abc123', project_id='123', completion_time=datetime.utcnow(), marked_num=0, skip_num=0, video_info='test_info', video_url='http://test.com/video.mp4')
        db.session.add(query)
        db.session.commit()
        assert Query.query.count() == 1

def test_user_project_model(test_app):
    with test_app.app_context():
        user_project = UserProject(user_project_id=1, project_id='123', user_id=1)
        db.session.add(user_project)
        db.session.commit()
        assert UserProject.query.count() == 1

def test_query_annotator_model(test_app):
    with test_app.app_context():
        query_annotator = QueryAnnotator(query_annotator_id=1, query_id='abc123', user_id=1)
        db.session.add(query_annotator)
        db.session.commit()
        assert QueryAnnotator.query.count() == 1
