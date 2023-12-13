from flask import Blueprint, jsonify
from ticket_overflow import ddb
import json

api = Blueprint('userAPI', __name__, url_prefix='/api/v1')
table = ddb.Table('Users')

@api.route('/users/health')
def health():
    return jsonify({"status":"ok"}), 200

@api.route('/users', methods=['GET'])
def get_users():
    items = table.scan()['Items']
    if len(items) == 0:
        with open("./ticket_overflow/users.json", "r") as dummyUsersFile:
                users = json.loads(dummyUsersFile.read())
                with table.batch_writer() as batch:
                        for user in users:
                                batch.put_item(Item=user)
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
        with open("./ticket_overflow/users.json", "r") as dummyUsersFile:
                users = json.loads(dummyUsersFile.read())
                with table.batch_writer() as batch:
                        for user in users:
                                batch.put_item(Item=user)
        return jsonify({"error": "user entry does not exist"}), 404
