from flask import Flask, request, jsonify
import boto3
import os
import pymysql

app = Flask(__name__)

# S3 설정
s3 = boto3.client(
    's3',
    aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
    region_name='ap-northeast-2'
)
S3_BUCKET = 'aws-solo-bucket64'

# DB 설정
db = pymysql.connect(
    host='10.0.2.179',
    user='flaskuser',
    password='Flask@ss2025!',
    database='flaskdb',
    cursorclass=pymysql.cursors.DictCursor
)

@app.route('/')
def index():
    return 'Flask S3 Upload System'

@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files.get('file')
    if not file:
        return jsonify({'error': 'No file uploaded'}), 400

    filename = file.filename
    s3.upload_fileobj(file, S3_BUCKET, filename)

    # DB 기록
    with db.cursor() as cursor:
        sql = "INSERT INTO uploads (filename) VALUES (%s)"
        cursor.execute(sql, (filename,))
        db.commit()

    return jsonify({'message': 'File uploaded', 'filename': filename}), 200

@app.route('/files', methods=['GET'])
def list_files():
    with db.cursor() as cursor:
        cursor.execute("SELECT id, filename, created_at FROM uploads ORDER BY created_at DESC")
        files = cursor.fetchall()
    return jsonify(files)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

