import logging
import json
import azure.functions as func
import azure.cosmos.cosmos_client as cosmos_client
from azure.cosmos.exceptions import CosmosHttpResponseError
import os


host = os.environ['ConnectionStrings:ACCOUNT_HOST']
key = os.environ['ConnectionStrings:ACCOUNT_KEY']

client = cosmos_client.CosmosClient(host, credential=key)
database = client.get_database_client('Quiplash')
container = database.get_container_client('players')


def main(req: func.HttpRequest, players: func.Out[func.Document]) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    logging.info("The JSON received {}".format(req.get_json()))
    req_body = req.get_json()
    req_body.update({
        "games_played": 0,
        'total_score': 0,
    })

    name = req_body.get('username')
    passw = req_body.get('password')

    same_name = container.query_items(
        query='SELECT * FROM players p WHERE p.username = @name',
        parameters=[
            dict(name='@name', value=name)
        ],
        enable_cross_partition_query=True
    )

    if len(name) < 4:
        return func.HttpResponse(
            json.dumps({
                "result": False,
                "msg": "Username less than 4 characters"
            }),
            mimetype="application/json"
        )

    if len(name) > 16:
        return func.HttpResponse(
            json.dumps({
                "result": False,
                "msg": "Username more than 16 characters"
            }),
            mimetype="application/json"
        )

    if len(passw) < 8:
        return func.HttpResponse(
            json.dumps({
                "result": False,
                "msg": "Password less than 8 characters"
            }),
            mimetype="application/json"
        )

    if len(passw) > 24:
        return func.HttpResponse(
            json.dumps({
                "result": False,
                "msg": "Password more than 24 characters"
            }),
            mimetype="application/json"
        )

    for row in same_name:
        return func.HttpResponse(
            json.dumps({
                "result": False,
                "msg": "Username already exists"
            }),
            mimetype="application/json"
        )

    # Inserting an account into cosmos
    try:
        players.set(func.Document.from_dict(req_body))

    except CosmosHttpResponseError:
        return func.HttpResponse("Something terrible happened....")

    return func.HttpResponse(
        json.dumps({
            "result": True,
            "msg": "OK"
        }),
        mimetype="application/json",
        status_code=200
    )
