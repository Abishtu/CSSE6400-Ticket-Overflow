from typing import Tuple, Dict
from flask import Blueprint, jsonify, request, Response
from boto3.dynamodb.conditions import Attr
from ticket_overflow import ddb
from ticket_overflow.util.Constants import CONCERT_URL, TICKET_URL, USER_URL
from ticket_overflow.util.Constants import CONCERT_SOLD_OUT
from ticket_overflow.util.Constants import TICKET_NOT_PRINTED, TICKET_PENDING,\
                                           TICKET_ERROR, TICKET_PRINTED
from ticket_overflow.models.Ticket import Ticket
from urllib.parse import urlparse

from .concert_service_routes import get_concert
from .user_service_routes import get_user

from ticket_overflow.tasks import hamilton
from celery.result import AsyncResult

import os


import time

api = Blueprint('ticketAPI', __name__, url_prefix='/api/v1')

table = ddb.Table('Tickets')
concertTable = ddb.Table('Tickets')

queryParameters = ("user_id", "concert_id")
dataFields = ("concert", "user", "print_status")

counter = {"asyncCount" : 0}

@api.route('/tickets/health')
def health() -> Tuple[Response, int]:
    return jsonify({"status":"ok"}), 200

@api.route('/tickets', methods=['GET'])
def get_tickets() -> Tuple[Response, int]:
    if request.args == {}:
        items = table.scan()['Items']
        return jsonify(items), 200
    
    if not set(request.args.keys()).issubset(set(queryParameters)):
        return jsonify({"error": "Invalid query!"}), 404
    
    args = list(request.args.keys())
    
    try:
        if len(args) == 2:
            response = table.scan(
                FilterExpression=Attr('concert.id').eq(request.args['concert_id']) & Attr('user.id').eq(request.args['user_id'])
            )
            if int(response["Count"]) == 0:
                return jsonify({"error": "entry not found"}), 404
            return jsonify(response["Items"]), 200
        
        if "concert_id" in args:
            response = table.scan(
                FilterExpression=Attr('concert.id').eq(request.args['concert_id'])
            )
            if int(response["Count"]) == 0:
                return jsonify({"error": "entry not found"}), 404
            return jsonify(response["Items"]), 200
        
        if "user_id" in args:
            response = table.scan(
                FilterExpression=Attr('user.id').eq(request.args['user_id'])
            )
            if int(response["Count"]) == 0:
                return jsonify({"error": "entry not found"}), 404
            return jsonify(response["Items"]), 200
    except KeyError as ke:
        return jsonify({"error": "entry not found"}), 404

    return str(request.args == {})

@api.route('/tickets', methods=['POST'])
def post_ticket() -> Tuple[Response, int]:
    try:
        concert = ""
        user = ""
        try:
            concert = request.json.get('concert_id')
            user = request.json.get('user_id')
        except KeyError as kE:
            return jsonify({"error": "request malformed, valid request" + \
                            " should only have concert_id and user_id"}), 400
        
        if not set(request.json.keys()).issubset(set(("concert_id",\
                                                    "user_id"))):
            return jsonify({"error": "request malformed, valid request" + \
                        " should only have two parameters"}), 400

        concert_response = get_concert(concert)
        user_response = get_user(user)

        concert_response_code = concert_response[1]
        user_response_code = user_response[1]
    
        if (concert_response_code == 404) or \
        (user_response_code == 404):
            return jsonify({"error": "request malformed, check if user" + \
                            f" or concert exist"}), 400
        response = table.scan(
                        FilterExpression=Attr('concert.id').eq(concert)
                   )
        
        # user_data = user_response[0].get_json()
        concert_data = concert_response[0].get_json()

        if (concert_data["status"] == CONCERT_SOLD_OUT):
            return jsonify({"error": "Ticket purchase failed, Sold out"}), 422

        if int(response["Count"]) == int(concert_data["capacity"]):
            table.update_item(
                Key={'id': concert},
                AttributeUpdates={
                    "status": {
                        'Value': CONCERT_SOLD_OUT,
                        'Action': 'PUT'
                    }
                }
            )

            return jsonify({"error": "Ticket purchase failed, Sold out"}), 422

        # concert_data.get_json()

        newTicket = Ticket(
            userID=user,
            concertID=concert,
            host=request.host_url,
            printStatus=TICKET_NOT_PRINTED
        )

        try:
            table.put_item(Item=newTicket.to_dict())
        except:
            return jsonify({"error": "unknown error, couldn't add to DB"}), 500
        
        return jsonify(newTicket.to_dict()), 201
    except Exception as e:
        return jsonify({"error": f"unknown error! {e}"}), 500

    # ADD TO DB

@api.route('/tickets/<id>', methods=['GET'])
def get_ticket(id: str) -> Tuple[Response, int]:
    response = table.get_item(
        Key={
            'id': id
        }
    )
    try:
        response["Item"]["id"] = id
        if response["Item"]["print_status"] == TICKET_PENDING:
            task_result = AsyncResult(id)
            if (task_result.status == "SUCCESS"):
                table.update_item (
                    Key={'id': id},
                    AttributeUpdates={
                        'print_status': {
                            'Value': TICKET_PRINTED,
                            'Action': 'PUT'
                        }
                    }
                )
        return jsonify(response["Item"]), 200
    except KeyError as ke:
        return jsonify({"error": "ticket entry does not exist"}), 404
    
"""
{
  "id": "12345678-1234-1234-1234-123456789012",
  "name": "Evan Hughes",
  "email": "example@uq.edu.au",
  "concert": {
    "id": "12345678-1234-1234-1234-123456789012",
    "name": "Phantom of the Opera",
    "date": "2023-06-07",
    "venue": "Sydney Opera House"
  }
}
"""
@api.route('/tickets/<id>/print', methods=['POST'])
def start_ticket_print(id: str) -> Tuple[Response, int]:
    response = table.get_item(
        Key={
            'id': id
        }
    )
    ticket = {}
    
    try:
        ticket = response["Item"]
    except KeyError as ke:
        return jsonify({"error": "ticket entry does not exist"}), 404
    if (ticket["print_status"] == TICKET_NOT_PRINTED):
        concert_data = ((get_concert((ticket["concert"])["id"]))[0]).get_json()
        user_data = ((get_user((ticket["user"])["id"]))[0]).get_json()

        hamiltonData = {
            "id": id,
            "name": user_data['name'],
            "email": user_data['email'],
            "concert": {
                "id": concert_data["id"],
                "name": concert_data["name"],
                "date": concert_data["date"],
                "venue": concert_data["venue"]
            }
        }

        try:
            output = hamilton.start_ticket_printing.apply_async(args=[hamiltonData], task_id=id)
            table.update_item (
            Key={'id': id},
            AttributeUpdates={
                    'print_status': {
                        'Value': TICKET_PENDING,
                        'Action': 'PUT'
                    }
                }
            )
        except Exception as e:
            return jsonify({"error": f"Unknown error occured, could not start printng {e}"}), 500
    
    return jsonify({"alert": "ticket is printing"}), 202

@api.route('/tickets/<id>/print', methods=['GET'])
def get_ticket_print(id: str):
    try:
        response = table.get_item(
            Key={
                'id': id
            }
        )
        ticket = response["Item"]
        if ticket["print_status"] == TICKET_NOT_PRINTED or \
            ticket["print_status"] == TICKET_ERROR:
            return jsonify({"error": "ticket entry does not exist"}), 404
        
        task_result = AsyncResult(id)
        if (task_result.status == "SUCCESS"):
            ticket["print_status"] = TICKET_PRINTED
            table.put_item(Item=ticket)
            ticket_svg = task_result.result
            task_result.forget()
            # task_result.revoke()
            with open(f"./out/ticket/{id}.svg", "w+") as cacheWriter:
                cacheWriter.write(ticket_svg)
            return ticket_svg, 200, {'Content-Type': 'image/svg+xml'}
        elif (ticket["print_status"] == TICKET_PRINTED):
            try:
                with open(f"out/ticket/{id}.svg", "r") as cacheReader:
                    output = cacheReader.read()
                return output, 200, {'Content-Type': 'image/svg+xml'}
            except FileNotFoundError as fee:
                return jsonify({"alert": f"ticket not printed!"}), 404
            
        else:
            return jsonify({"alert": f"ticket not printed!"}), 404
    except KeyError as ke:
        return jsonify({"error": "ticket entry does not exist"}), 404
        