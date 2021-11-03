import logging
import json
import azure.functions as func
import azure.cosmos.cosmos_client as cosmos_client
import os
import random


host = os.environ['ConnectionStrings:ACCOUNT_HOST']
key = os.environ['ConnectionStrings:ACCOUNT_KEY']

client = cosmos_client.CosmosClient(host, credential=key)
database = client.get_database_client('Quiplash')
container = database.get_container_client('prompts')


def format_json(n):
    n["id"] = n.pop("id_p")
    n["text"] = n.pop("text")
    n["username"] = n.pop("username")
    return n


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')
    logging.info("The JSON received {}".format(req.get_json()))
    req_body = req.get_json()
    inputt = req_body.get('players')

    list1 = []
    if inputt == -1:
        items = container.query_items(
            query='SELECT p.id_p, p.text, p.username FROM prompts p',
            enable_cross_partition_query=True
        )

        for row in items:
            list1.append(row)

    else:
        for name in inputt:
            items = container.query_items(
                query='SELECT p.id_p, p.text, p.username FROM prompts p WHERE p.username = @name',
                parameters=[
                    dict(name='@name', value=name)
                ],
                enable_cross_partition_query=True
            )

            for row in items:
                list1.append(row)

    list2 = json.dumps(list1)
    return func.HttpResponse(list2)
