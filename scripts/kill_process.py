import os
import psutil
import signal

def kill_process_by_name(process_name):
    for proc in psutil.process_iter(['pid', 'name']):
        if process_name in proc.info['name']:
            print(f"Terminating process {proc.info['pid']} - {proc.info['name']}")
            os.kill(proc.info['pid'], signal.SIGTERM)

if __name__ == '__main__':
    # Specify the process names to be terminated
    process_names = ['celery', 'python', 'npm']

    for process_name in process_names:
        kill_process_by_name(process_name)