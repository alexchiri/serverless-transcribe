import logging
import boto3
import tempfile
import requests
import os
from urllib.parse import unquote, urlparse, parse_qsl

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


def upload_podcast_to_s3(event):
    body = event['body']
    s3 = boto3.client('s3')
    parameters = dict(parse_qsl(body))
    logger.debug(f"Parameters received from form: {parameters}")

    if not parameters or parameters.__len__() < 3:
        return {
            'statusCode': 500,
            'error': {
                'description': 'Form data was not posted!',
            }
        }
    else:
        podcast_url = parameters['upload_url']
        logger.warning(f"Podcast URL: {podcast_url}")

        with tempfile.NamedTemporaryFile() as file:
            response = requests.get(podcast_url, stream=True)
            logger.warning(f"Status code from requests: {response.status_code}")
            logger.warning(f"Temporary file name: {file.name}")

            for chunk in response.iter_content(chunk_size=512):
                if chunk:
                    file.write(chunk)

            parsed_url = urlparse(podcast_url)
            logger.warning(f"Parsed URL: {parsed_url}")
            logger.warning(f"Parsed path: {parsed_url.path}")

            file_name = os.path.basename(parsed_url.path)
            logger.warning(f"Downloaded file name: {file_name}")
            s3.upload_file(file.name, os.environ['MEDIA_BUCKET'], file_name, ExtraArgs={
                "Metadata": {"email": f"{parameters['email']}",
                             "maxspeakerlabels": f"{parameters['maxspeakerlabels']}"}})

    return {
        'statusCode': 200,
        'body': '{ "success": true}'
    }


def lambda_handler(event, context):
    try:
        response = upload_podcast_to_s3(event)
    except Exception as error:
        logger.exception(error)
        response = {
            'statusCode': 500,
            'error': {
                'type': type(error).__name__,
                'description': str(error),
            },
        }

    return response
