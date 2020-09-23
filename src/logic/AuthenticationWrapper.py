from functools import wraps

from flask import request, jsonify


def require_api_key(password):
    def wrap_route(func):
        @wraps(func)
        def check_api_key(*args, **kwargs):
            apiKey = request.headers.get('apiKey')
            if not apiKey:
                return jsonify({'message': 'apiKey missing'}), 401

            if apiKey == password:
                # redirect to requested url
                return func(*args, **kwargs)

            return jsonify({'message': 'apiKey invalid'}), 401

        return check_api_key

    return wrap_route
