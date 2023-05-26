import json
import boto3
from rembg import remove
from PIL import Image
from io import BytesIO
import os
from flask import Flask, request
import requests

app = Flask(__name__)


@app.route('/products', methods=['POST'])
def removebackground():
    data = request.get_json()
    image_url = data["image_url"]
    image_key = data["image_key"]
    bucket_name = data["bucket_name"]

    os.makedirs('/tmp/original', exist_ok=True)
    os.makedirs('/tmp/masked', exist_ok=True)

    img_name = image_key
    img_path = f'/tmp/original/{img_name}'
    output_path = f'/tmp/masked/{img_name}'

    img = Image.open(BytesIO(requests.get(image_url).content))
    img.save(img_path)

    with open(output_path, 'wb') as f:
        with open(img_path, 'rb') as input_file:
            subject = remove(input_file.read(), alpha_matting=True, alpha_matting_foreground_threshold=240)
            f.write(subject)

    upload_image_to_s3(output_path, bucket_name, image_key, img_path)


def upload_image_to_s3(file_path, bucket_name, image_key, img_path):
    try:
        s3 = boto3.client('s3')
        with open(file_path, 'rb') as file:
            s3.upload_fileobj(file, bucket_name, "output/" + image_key, ExtraArgs={'ContentType': "image"})
        print(f"Successfully uploaded {file_path} to {bucket_name}/{image_key}")
    except Exception as e:
        print(f"Error uploading {file_path} to {bucket_name}/{image_key}: {str(e)}")
    finally:
        os.remove(file_path)
        os.remove(img_path)
        folder_path = '/tmp/original/'
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)

        if os.path.isfile(file_path):
            print(filename)

    # Check if the path is a file (not a directory)
    if os.path.isfile(file_path):
        print(filename)

    return {
        'statusCode': 200,
        'body': json.dumps({"message": "success"}),
    }


if __name__ == "__main__":
    app.run(port=5000, debug=True)
