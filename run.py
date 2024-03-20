import os
import time
import multiprocessing

"""
    function for start celery
"""
def run_celery():
    os.system("echo Starting celery ...")
    os.system("celery -A uni_rlhf.controllers.auth.celery worker -l INFO")

"""
    function for start Flask server
"""
def run_flask_server(flask_port):
    os.system(f"echo Starting Flask server on http://localhost:{flask_port}/ ...")
    os.system(f"python -m uni_rlhf.controllers.auth --port {flask_port}")
    
"""
    function for start vue server
"""
def run_vue_server(vue_port):
    time.sleep(8)
    os.system("echo Starting vue server ...")
    os.system(f"npm run serve --prefix ./uni_rlhf/vue_part/ -- --port {vue_port}")


if __name__ == '__main__':
    """
        Run Backend Server & Frontend Server at the same time.
    """
    flask_port = 8502 
    vue_port = 8503
    
    p1 = multiprocessing.Process(target=run_celery)
    p2 = multiprocessing.Process(target=run_flask_server, args=(flask_port,))
    p3 = multiprocessing.Process(target=run_vue_server, args=(vue_port,))

    p1.start()
    p2.start()
    p3.start()

    p1.join()
    p2.join()
    p3.join()