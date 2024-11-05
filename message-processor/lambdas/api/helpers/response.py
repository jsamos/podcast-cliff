import json

def response(status_code, body):
    return {
        'statusCode': status_code,
        'body': json.dumps(body),
        'headers': {'Content-Type': 'application/json'}
    }

def error_response(message):
    return response(500, {'message': message})

def success_response(body, status_code=200):
    return response(status_code, body)

def no_content_response():
    return response(204, '')

def not_found():
    return response(404, {'message': 'Item not found'})