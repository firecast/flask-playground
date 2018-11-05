from flask import Flask, current_app, request

app = Flask(__name__)


@app.route('/')
def index():
    seen = request.cookies.get('seen', False)
    resp = 'Hello, {} friend'.format('old' if seen else 'new')
    response = current_app.make_response(resp)
    response.set_cookie(
        'seen', 'yes', max_age=3600, path='/', secure=True, httponly=True)
    return response
