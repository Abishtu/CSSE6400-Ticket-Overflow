import logging
import os
import subprocess
import time
import json

from ticket_overflow.util.Constants import HAMILTON_TICKET_GEN, \
                                           HAMILTON_SEATING_GEN

from celery import Celery
from kombu.utils.url import safequote

aws_access_key = safequote(os.environ.get("AWS_ACCESS_KEY"))
aws_secret_key = safequote(os.environ.get("AWS_SECRET_KEY"))
aws_region = safequote(os.environ.get("AWS_REGION"))

celery = Celery(__name__)
# celery.conf.broker_url = os.environ.get("CELERY_BROKER_URL")
# celery.conf.result_backend = os.environ.get("CELERY_RESULT_BACKEND")
# celery.conf.task_default_queue = os.environ.get("CELERY_DEFAULT_QUEUE",
#                                                 "hamilton")

# celery.conf.broker_url = f"sqs://{aws_access_key}:{aws_secret_key}@{aws_region}"
# celery.conf.task_default_queue = "hamilton_tasks"
# celery.conf.broker_transport_options = {
#         "predefined_queues": {
#             "hamilton_tasks": {
#                 "url": "https://sqs.ap-southeast-2.amazonaws.com/951094886160/hamilton-tasks"
#             }
#         },
#         "region": aws_region
#     }
# celery.conf.result_backend = None
# celery.conf.task_default_queue = os.environ.get("CELERY_DEFAULT_QUEUE",
#                                                 "hamilton")

logger = logging.getLogger(__name__)

logger.warning(os.environ.get("AWS_ACCESS_KEY_ID"))
logger.warning(os.environ.get("AWS_SECRET_ACCESS_KEY"))

logger.warning(aws_access_key)
logger.warning(aws_secret_key)

def run_hamilton_generation(option: str, id: str):
    file_gen = subprocess.Popen(["./bin/hamilton", 'generate', 
                                 option, '--input', 
                                f'./out/{option}/{id}.json', 
                                 '--output', 
                                f'./out/{option}/{id}'],
                                stdout=subprocess.PIPE)
    output, error = file_gen.communicate()
    file_gen.wait()

    return f'./out/{option}/{id}.svg', output, error

@celery.task(name="concerts")
def get_seat_layout(input_data):
    id = input_data["id"]
    hamiltonData = json.dumps(input_data)
    existingData = {}
    try:
        existingFile = open(f"out/seating/{id}.json", "r")
        existingData = json.load(existingFile)
        existingFile.close()
        if existingData == input_data:
            existingSvg = open(f"out/seating/{id}.svg", "r")
            seats = existingSvg.read()
            existingSvg.close()
            return seats
        else:
            with open(f"out/seating/{id}.json", "w") as modifyFile:
                modifyFile.writelines(hamiltonData)
            modifyFile.close()
    except FileNotFoundError:
        with open(f"out/seating/{id}.json", "w+") as inputDataWriter:
            inputDataWriter.writelines(hamiltonData)
        inputDataWriter.close()

    fileName, output, error = run_hamilton_generation(HAMILTON_SEATING_GEN, 
                                                    id)
    with open(fileName, "r") as svgReader:
        seatingSVG = svgReader.read()
    svgReader.close()
    return seatingSVG

@celery.task(name="tickets")
def start_ticket_printing(input_data):
    id = input_data["id"]
    hamiltonData = json.dumps(input_data)
    existingData = {}
    try:
        existingFile = open(f"out/ticket/{id}.json", "r")
        existingData = json.load(existingFile)
        existingFile.close()
        if existingData == input_data:
            existingSvg = open(f"out/ticket/{id}.svg", "r")
            seats = existingSvg.read()
            existingSvg.close()
            return seats
        else:
            with open(f"out/ticket/{id}.json", "w") as modifyFile:
                modifyFile.writelines(hamiltonData)
            modifyFile.close()
    except FileNotFoundError:
        with open(f"out/ticket/{id}.json", "w+") as inputDataWriter:
            inputDataWriter.writelines(hamiltonData)
        inputDataWriter.close()

    fileName, output, error = run_hamilton_generation(HAMILTON_TICKET_GEN, 
                                                      id)
    with open(fileName, "r") as svgReader:
        seatingSVG = svgReader.read()
    svgReader.close()
    return seatingSVG

@celery.task(name="returnsmaeticket")
def return_printed_ticket(id:str):
    try:
        with open(f"out/ticket/{id}.svg", "r") as svgReader:
            seatingSVG = svgReader.read()
        svgReader.close()
        return seatingSVG
    except FileNotFoundError as fee:
        return "ticket not printed!"
@celery.task(name="cachereset")
def cache_reset(ticket_ids, concert_ids):
    for ticket_id in ticket_ids:
        try:
            ticket_path = os.path.join("out/ticket", f"{ticket_id}.svg")
            os.remove(ticket_path)
            logger.info(f"{ticket_id}.svg removed")
        except:
            logger.info(f"{ticket_id}.svg not removed")
    for concert_id in concert_ids:
        try:
            seating_path = os.path.join("out/ticket", f"{concert_id}.svg")
            os.remove(seating_path)
            logger.info(f"{concert_id}.svg removed")
        except:
            logger.info(f"{concert_id}.svg not removed")
    
    return "cache cleared"
