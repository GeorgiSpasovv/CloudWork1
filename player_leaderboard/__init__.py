import logging
import json

from azure.core.tracing.decorator import distributed_trace
import azure.functions as func
import azure.cosmos.cosmos_client as cosmos_client
from azure.cosmos.exceptions import CosmosHttpResponseError
import os


host = os.environ['ConnectionStrings:ACCOUNT_HOST']
key = os.environ['ConnectionStrings:ACCOUNT_KEY']

client = cosmos_client.CosmosClient(host, credential=key)
database = client.get_database_client('Quiplash')
container = database.get_container_client('players')


def format_json(n):
    n["username"] = n.pop("username")
    n["score"] = n.pop("total_score")
    n["games_played"] = n.pop("games_played")
    return n


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    logging.info("The JSON received {}".format(req.get_json()))
    req_body = req.get_json()

    k = int(req_body.get('top'))

    db_item = container.query_items(
        query='SELECT TOP @name p.username, p.total_score, p.games_played FROM players p',
        parameters=[
            dict(name='@name', value=k)
        ],
        enable_cross_partition_query=True
    )

    list1 = []
    for row in db_item:
        list1.append(format_json(row))

    list2 = json.dumps(
        sorted(list1, key=lambda d: (-d['score'], d['username'])))
    return func.HttpResponse(list2)
