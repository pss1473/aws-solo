from flask import Flask, request, jsonify
import boto3
import os
from botocore.exceptions import BotoCoreError, ClientError

app = Flask(__name__)

S3_BUCKET = "aws-solo-bucket64"
S3_REGION = "ap-northeast-2"

s3 = boto3.client(
    "s3",
    aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY"),
    region_name=S3_REGION
)

@app.route('/')
def hello():
    return '✅ Hello from Flask in Docker on Private EC2!'

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in request'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    try:
        s3.upload_fileobj(file, S3_BUCKET, file.filename)
        file_url = f"https://{S3_BUCKET}.s3.{S3_REGION}.amazonaws.com/{file.filename}"
        return jsonify({'message': '✅ Upload successful', 'url': file_url}), 200
    except (BotoCoreError, ClientError) as e:
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
