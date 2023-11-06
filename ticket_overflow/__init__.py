from flask import Flask
import boto3
from ticket_overflow.models.Concert import Concert
from ticket_overflow.models.Ticket import Ticket
from ticket_overflow.models.User import User
import json

import os

"""
DynamoDB setup:
1. Get DynamoDB local
2. Get boto3 pip package
"""
# Create resource
os.environ['AWS_SHARED_CREDENTIALS_FILE'] = 'credentials'
ddb_session = boto3.Session()
ddb = ddb_session.resource('dynamodb', region_name='us-east-1')    

def create_app():
    app = Flask(__name__)
    
    try:
        # Adding in list of users for testing
        userTable = ddb.Table('Users')
        with open("./ticket_overflow/users.json", "r") as dummyUsersFile:
                users = json.loads(dummyUsersFile.read())
                with userTable.batch_writer() as batch:
                        for user in users:
                                batch.put_item(Item=user)
    except Exception as e:
        pass

    # Register the blueprints
    from ticket_overflow.views.\
         concert_service_routes \
            import api as concertAPI
    from ticket_overflow.views.\
         ticket_service_routes \
            import api as tApi
    from ticket_overflow.views.\
         user_service_routes \
            import api as uApi

    app.register_blueprint(concertAPI)
    app.register_blueprint(tApi)
    app.register_blueprint(uApi)

    return app