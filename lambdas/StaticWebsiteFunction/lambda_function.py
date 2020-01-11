import logging

logger = logging.getLogger()
logger.setLevel(logging.WARNING)


def render_static_website():

    return {
        'statusCode': 200,
        'headers': {'content-type': 'text/html'},
        'body': open('index.html', 'r', encoding='utf-8').read()
    }


def lambda_handler(event, context):
    try:
        response = render_static_website()
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
