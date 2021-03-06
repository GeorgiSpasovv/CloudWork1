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


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    logging.info("The JSON received {}".format(req.get_json()))
    req_body = req.get_json()

    name = req_body.get('username')
    passw = req_body.get('password')

    db_item = container.query_items(
        query='SELECT * FROM players p WHERE p.username = @name',
        parameters=[
            dict(name='@name', value=name)
        ],
        enable_cross_partition_query=True
    )

    for row in db_item:
        db_passw = row.get('password')
        if db_passw == passw:
            return func.HttpResponse(
                json.dumps({
                    "result": True,
                    "msg": "OK"
                }),
                mimetype="application/json",
                status_code=200
            )

    return func.HttpResponse(
        json.dumps({
            "result": False,
            "msg": "Username or password incorrect"
        }),
        mimetype="application/json"

    )
