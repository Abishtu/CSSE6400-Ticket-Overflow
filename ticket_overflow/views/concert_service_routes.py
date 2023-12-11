from flask import Blueprint, jsonify, request
from ticket_overflow import ddb
from ticket_overflow.models.Concert import Concert
from ticket_overflow.util.Constants import CONCERT_STATUS, DATE_FORMAT, CONCERT_SOLD_OUT, TICKET_NOT_PRINTED
from datetime import datetime

from ticket_overflow.tasks import hamilton
from boto3.dynamodb.conditions import Attr


api = Blueprint('concertAPI', __name__, url_prefix='/api/v1')
table = ddb.Table('Concerts')
ticketsTable = ddb.Table('Tickets')
dataFields = ('name', 'venue', 'date', 'capacity', 'status')

@api.route('/concerts/health')
def health():
    return jsonify({"status":"ok"}), 200

@api.route('/concerts', methods=['GET'])
def get_concerts():
    items = table.scan()['Items']
    for item in items:
        item["capacity"] = int(item["capacity"])
    return jsonify(items), 200

@api.route('/concerts', methods=['POST'])
def post_concert():
    try:
        if "name" not in request.json:
            return jsonify({"error": "Missing title"}), 400
        elif type(request.json.get('name')) is not str:
            return jsonify({"error": "Name is supposed to be a string"}), 400
        
        if "venue" not in request.json:
            return jsonify({"error": "Missing venue"}), 400
        elif type(request.json.get('venue')) is not str:
            return jsonify({"error": "Venue is supposed to be a string"})
        
        if "date" not in request.json:
            return jsonify({"error": "Missing date"}), 400
        else:
            date = request.json.get("date")
            try:
                datetime.strptime(date, DATE_FORMAT).date()
            except ValueError as vE:
                return jsonify({"error": f"Malformed date, {date} not in %Y-%m-%d"}), 400
            
        if "capacity" not in request.json:
            return jsonify({"error": "Missing capacity"}), 400
        elif type(request.json.get("capacity")) is not int:
            return jsonify({"error": "Capacity is supposed to be an integer"}), 400
        elif request.json.get("capacity") < 0:
                return jsonify({"error": "Capacity is supposed to be a integer >= 0"}), 400
        
        if "status" not in request.json:
            return jsonify({"error": "Missing status"}), 400
        elif request.json.get("status") not in CONCERT_STATUS:
            return jsonify({"error": "Invalid status code"}), 400
        
        if not set(request.json.keys()).issubset(set(dataFields)):
            return jsonify({"error": "Extra fields"}), 400
        # Add to DB
        newConcert = Concert (
            name = request.json.get("name"),
            venue = request.json.get("venue"),
            date = request.json.get("date"),
            status = request.json.get("status"),
            capacity = request.json.get("capacity") 
        )

        inputEntry = newConcert.to_dict()

        table.put_item(Item=inputEntry)
        
        return jsonify(inputEntry), 201
    except Exception as e:
        return jsonify({"error": f"{e}"}), 500

@api.route('/concerts/<id>', methods=['GET'])
def get_concert(id:str):
    response = table.get_item(
        Key={
            'id': id
        }
    )
    try:
        outputDict = response["Item"]
        outputDict["capacity"] = int(outputDict["capacity"])
        return jsonify(outputDict), 200
    except KeyError as ke:
        return jsonify({"error": f"concert entry does not exist."}), 404

"""
import boto3

table = boto3.resource('dynamodb').Table('my_table')

table.update_item(
    Key={'pkey': 'asdf12345'},
    AttributeUpdates={
        'status': 'complete',
    },
)
"""
@api.route('/concerts/<id>', methods=['PUT'])
def put_concert(id:str):
    try:
        response = table.get_item(
            Key={
                'id': id
            }
        )
        try:
            response["Item"]
        except KeyError as ke:
            return jsonify({"error": "concert entry does not exist"}), 404
        if not set(request.json.keys()).issubset(set(("name", "venue", "date", "status"))):
            return jsonify({"error": "Extra fields"}), 400
        
        if "name" in request.json:
            if type(request.json.get('name')) is not str:
                return jsonify({"error": "Name is supposed to be a string"}), 400
        
        if "venue" in request.json:
            if type(request.json.get('venue')) is not str:
                return jsonify({"error": "Venue is supposed to be a string"})
        
        if "date" in request.json:
            date = request.json.get("date")
            try:
                datetime.strptime(date, DATE_FORMAT).date()
            except ValueError as vE:
                return jsonify({"error": f"Malformed date, {date} not in %Y-%m-%d"}), 400

        if "status" in request.json:
            if request.json.get("status") not in CONCERT_STATUS:
                return jsonify({"error": "Invalid status code"}), 400

        updateQuery = request.json
        for key in request.json.keys():
            updateQuery[key] = {
                'Value': request.json.get(key),
                'Action': 'PUT'
            }
        
        table.update_item(
            Key={'id': id},
            AttributeUpdates=updateQuery
        )

        # Get updated table
        response = table.get_item(
            Key={
                'id': id
            }
        )
        # Get tickets if they exist
        try:
            tickets = ticketsTable.scan(
                FilterExpression=Attr('concert.id').eq(id)
            )
            if int(tickets["Count"]) > 0:
                ticket_ids = []
                for ticket in tickets["Items"]:
                    ticketsTable.update_item(
                        Key={'id': ticket["id"]},
                        AttributeUpdates={
                            'print_status': {
                                'Value': TICKET_NOT_PRINTED,
                                'Action': 'PUT'
                            }
                        }
                    )
                    ticket_ids.append(ticket["id"])
                output = hamilton.cache_reset(ticket_ids, [id])
        except:
            pass
        try:
            response["Item"]["id"] = id
            response["Item"]["capacity"] = int(response["Item"]["capacity"])
            return jsonify(response["Item"]), 200
        except KeyError as ke:
            return jsonify({"error": "concert entry does not exist"}), 404
    except Exception as e:
        return jsonify({"error": f"unknown error occured, {e}"}), 500
"""
{
  "id": "12345678-1234-1234-1234-123456789012",
  "name": "Phantom of the Opera",
  "date": "2023-06-07",
  "venue": "Sydney Opera House",
  "seats": {
    "max": 5738,
    "purchased": 2340
  }
}
"""
@api.route('/concerts/<id>/seats', methods=['GET'])
def get_concert_seats(id:str):
    concert = {}
    response = table.get_item(
        Key={
            'id': id
        }
    )
    try:
        concert = response["Item"]
    except KeyError as ke:
        return jsonify({"error": "concert entry does not exist"}), 404

    bookingCount = ticketsTable.scan(
        FilterExpression=Attr('concert.id').eq(id)
    )['Count']
    if bookingCount == int(concert['capacity']):
        table.update_item(
            Key={'id': id},
            AttributeUpdates={
                'status': {
                    'Value': CONCERT_SOLD_OUT,
                    'Action': 'PUT'
                }
            }
        )
    hamiltonData = {
        "id": id,
        "name": concert['name'],
        "date": concert['date'],
        "venue": concert['venue'],
        "seats": {
            "max": int(concert['capacity']),
            "purchased": bookingCount
        }
    }

    output = hamilton.get_seat_layout(hamiltonData)
    return output, 200, {'Content-Type': 'image/svg+xml'}