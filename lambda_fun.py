import boto3
import requests
from urllib.parse import unquote

remove_bg_url = 'http://localhost:5000'


def handler(event, context):
    print("running function")

    s3_client = boto3.client('s3')
    print(event)
    bucket_name = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']

    if "input/" in key:
        keys = key.split("/")[1]

    message = f"Hey, this file {key} got uploaded to bucket {bucket_name}"
    print(message)

    image_url = s3_client.generate_presigned_url(
        'get_object',
        Params={'Bucket': bucket_name, 'Key': key},
    )
    img_url = unquote(image_url.split("?")[0])
    print("Image URL:", img_url)

    image_data = {
        'image_url': image_url,
        'image_key': keys,
        'bucket_name': bucket_name
    }

    requests.post(f'{remove_bg_url}/products', json=image_data)

    print(event)
