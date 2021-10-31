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
container1 = database.get_container_client('players')
container2 = database.get_container_client('prompts')


def main(req: func.HttpRequest, prompts: func.Out[func.Document]) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    logging.info("The JSON received {}".format(req.get_json()))
    req_body = req.get_json()
    text = req_body.get('text')
    name = req_body.get('username')
    passw = req_body.get('password')
    status = False

    db_user = container1.query_items(
        query='SELECT * FROM players p WHERE p.username = @name',
        parameters=[
            dict(name='@name', value=name)
        ],
        enable_cross_partition_query=True
    )

    for row in db_user:
        db_passw = row.get('password')
        if db_passw == passw:
            status = True

    if status:
        if len(text) < 10:
            return func.HttpResponse(
                json.dumps({
                    "result": False,
                    "msg": "prompt is less than 10 characters"
                }),
                mimetype="application/json"
            )

        if len(text) > 100:
            return func.HttpResponse(
                json.dumps({
                    "result": False,
                    "msg": "prompt is more than 100 characters"
                }),
                mimetype="application/json"
            )

        db_prompt = container2.query_items(
            query='SELECT * FROM prompts p WHERE p.text = @name',
            parameters=[
                dict(name='@name', value=text)
            ],
            enable_cross_partition_query=True
        )

        for line in db_prompt:
            return func.HttpResponse(
                json.dumps({
                    "result": False,
                    "msg": "User already has a prompt with the same text"
                }),
                mimetype="application/json"
            )

        db_el = container2.query_items(
            query='SELECT TOP 1 * FROM prompts p ORDER BY p.id_p DESC',
            enable_cross_partition_query=True
        )

        id_p = 1

        for r in db_el:
            id_p = r.get('id_p') + 1

        # Inserting a prompt into cosmos

        prompt = {
            "id_p": id_p,
            "username": name,
            "text": text
        }
        try:
            prompts.set(func.Document.from_dict(prompt))

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

    return func.HttpResponse(
        json.dumps({
            "result": False,
            "msg": "bad username or password"
        }),
        mimetype="application/json"

    )
