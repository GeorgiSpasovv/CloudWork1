import logging
import json

from azure.core.tracing.decorator import distributed_trace
import azure.functions as func
import azure.cosmos.cosmos_client as cosmos_client
from azure.cosmos.exceptions import CosmosHttpResponseError
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
    n = req_body.get('n')

    items = container.query_items(
        query='SELECT p.id_p, p.text, p.username FROM prompts p',
        enable_cross_partition_query=True
    )

    random_numbers = set()
    items_list = []
    for j, r in enumerate(items):
        items_list.append(r)

    strr = ""
    i = 0
    if n > len(items_list):
        n = len(items_list)

    while i < n:
        k = random.randint(0, len(items_list)-1)
        if k not in random_numbers:
            strr = strr + json.dumps(format_json(items_list[k])) + ", "
            random_numbers.add(k)
            i += 1

    strr = "[" + strr + "]"

    return func.HttpResponse(strr)
