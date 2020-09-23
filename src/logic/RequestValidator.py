from typing import Dict, List

from flask import jsonify


class ValidationError(Exception):
    def __init__(self, message):
        super().__init__(message)
        self.response = jsonify({'success': False,
                                 'msg': message})


class RequestValidator:
    @staticmethod
    def validate(request, parameters: List[str]) -> Dict:
        if not request.is_json:
            raise ValidationError('Missing JSON in request')

        return RequestValidator.validate_parameters(request.json, parameters, 'request')

    @staticmethod
    def validate_parameters(data: Dict, parameters: List[str], itemName: str) -> Dict:
        result = {}
        for param in parameters:
            value = data.get(param, None)
            if value is None:
                raise ValidationError(f'Missing parameter "{param}" for {itemName}')
            result[param] = value
        return result
