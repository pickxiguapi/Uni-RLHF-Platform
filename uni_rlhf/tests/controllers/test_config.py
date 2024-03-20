import pytest
from uni_rlhf.config import create_app

class TestConfig:
    def test_app_config(self):
        """ 测试应用配置是否正确加载 """

        app = create_app()

        # 测试数据库配置
        assert app.config['SQLALCHEMY_DATABASE_URI'] == 'your database'
        assert app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] is False

        # 测试Celery配置
        assert app.config['CELERY_BROKER_URL'] == 'redis://localhost:6379/0'
        assert app.config['CELERY_RESULT_BACKEND'] == 'redis://localhost:6379/0'

        # 测试应用密钥
        assert app.secret_key == 'your_secret_key'
