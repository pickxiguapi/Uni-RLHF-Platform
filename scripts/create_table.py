import pymysql

cfg = {
    'host': 'your_host',
    'port': 3306,
    'username': 'your_username',
    'password': 'your_password',
    'database_name': 'your_database_name'
}

try:
    connection = pymysql.connect(
        host=cfg['host'],
        user=cfg['username'],
        password=cfg['password'],
        database=cfg['database_name']
    )
    cursor = connection.cursor()
    # logger.Logger.info('[database] successfully connect database!')
except pymysql.err.OperationalError as e:
    # If the connection fails, determine whether to create a new database based on the error code
    if e.args[0] == 1049:  # Could not find database
        connection = pymysql.connect(
            host=cfg['host'],
            user=cfg['username'],
            password=cfg['password']
        )
        cursor = connection.cursor()
        cursor.execute(f"CREATE DATABASE {cfg['database_name']}")
        cursor.execute(f"USE {cfg['database_name']}")
        # logger.Logger.info(f"[database] Database {cfg['database_name']} created and connected")
    else:
        # If it is not because the database was not found, the error is thrown again
        raise e

sql1='''CREATE TABLE IF NOT EXISTS User (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    password VARCHAR(255) NOT NULL,
    email VARCHAR(100) NOT NULL,
    is_authenticated BOOLEAN,
    is_active BOOLEAN,
    is_anonymous BOOLEAN,
    avatar VARCHAR(50),
    is_deleted BOOLEAN DEFAULT 0
    
);'''
cursor.execute(sql1)


sql2='''CREATE TABLE IF NOT EXISTS Project(

project_id VARCHAR(100) PRIMARY KEY,
project_name VARCHAR(100) NOT NULL,
description TEXT,
due_time DATETIME NOT NULL,
visibility BOOLEAN NOT NULL,
dataset_path VARCHAR(100),
domain VARCHAR(100),
task VARCHAR(100),
environment_name VARCHAR(100),
instruction TEXT NOT NULL,
mode VARCHAR(100) NOT NULL,
sampler_type VARCHAR(50) NOT NULL,
feedback_type VARCHAR(50) NOT NULL,
query_num INT NOT NULL,
query_length INT NOT NULL,
video_width INT NOT NULL,
video_height INT NOT NULL,
fps INT NOT NULL,
creator INT NOT NULL,
create_time datetime NOT NULL,
status VARCHAR(100) NOT NULL,
annotation_num INT NOT NULL,
question json NOT NULL,
is_deleted BOOLEAN DEFAULT 0,
FOREIGN KEY (creator) REFERENCES User(user_id)

);'''
cursor.execute(sql2)


sql3='''CREATE TABLE IF NOT EXISTS UserProject (

user_project_id INT AUTO_INCREMENT PRIMARY KEY,
project_id VARCHAR(100) NOT NULL,
user_id INT NOT NULL,
is_deleted BOOLEAN DEFAULT 0,
FOREIGN KEY (user_id) REFERENCES User(user_id),
FOREIGN KEY (project_id) REFERENCES Project(project_id)

);'''
cursor.execute(sql3)



sql4='''CREATE TABLE IF NOT EXISTS Query (

query_id VARCHAR(100) PRIMARY KEY,
project_id VARCHAR(100) NOT NULL,
completion_time datetime,
marked_num INT DEFAULT 0,
skip_num INT DEFAULT 0,
video_info json DEFAULT NULL,
label_info json DEFAULT NULL,
video_url TEXT DEFAULT NULL,
is_deleted BOOLEAN DEFAULT 0,
FOREIGN KEY (project_id) REFERENCES Project(project_id)

);'''
cursor.execute(sql4)



sql5='''CREATE TABLE IF NOT EXISTS QueryAnnotator (

query_annotator_id INT AUTO_INCREMENT PRIMARY KEY,
query_id VARCHAR(100) NOT NULL,
user_id INT NOT NULL,
is_deleted BOOLEAN DEFAULT 0,
FOREIGN KEY (query_id) REFERENCES Query(query_id),
FOREIGN KEY (user_id) REFERENCES User(user_id)

);'''
cursor.execute(sql5)
