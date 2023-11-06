from flask import Blueprint, jsonify
from ticket_overflow import ddb

api = Blueprint('userAPI', __name__, url_prefix='/api/v1')
table = ddb.Table('Users')

@api.route('/users/health')
def health():
    return jsonify({"status":"ok"}), 200

@api.route('/users', methods=['GET'])
def get_users():
    items = table.scan()['Items']
    return jsonify(items), 200

@api.route('/users/<id>', methods=['GET'])
def get_user(id):
    response = table.get_item(
        Key={
            'id': id
        }
    )
    try:
        return jsonify(response["Item"]), 200
    except KeyError as ke:
        return jsonify({"error": "user entry does not exist"}), 404