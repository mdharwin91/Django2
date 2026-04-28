import os

def creds():
    secrets = {}
    secrets['accessKey'] = os.environ.get('AWS_KEY_ID')
    secrets['secretKey'] = os.environ.get('AWS_SECRET_KEY')
    secrets['region'] = os.environ.get('AWS_REGION', 'ap-south-1')
    return secrets
