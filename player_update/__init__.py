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
    req_body = req.get_json()

    name = req_body.get('username')
    passw = req_body.get('password')
    add_to_games_played = req_body.get('add_to_games_played')
    add_to_score = req_body.get('add_to_score')

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

            if add_to_games_played:
                row['games_played'] += int(add_to_games_played)

                if int(row['games_played']) < 0:
                    return func.HttpResponse(
                        json.dumps({
                            "result": False,
                            "msg": "Attempt to set negative score/games_played"
                        }),
                        mimetype="application/json"

                    )

                # if int(add_to_games_played) < 0:
                #     return func.HttpResponse(
                #         json.dumps({
                #             "result": False,
                #             "msg": "Attempt to set negative score/games_played"
                #         }),
                #         mimetype="application/json"

                #     )

                # else:
                #     row['games_played'] += int(add_to_games_played)

            if add_to_score:
                row['total_score'] += int(add_to_score)

                if int(row['total_score']) < 0:
                    return func.HttpResponse(
                        json.dumps({
                            "result": False,
                            "msg": "Attempt to set negative score/games_played"
                        }),
                        mimetype="application/json"
                    )
                # if int(add_to_score) < 0:
                #     return func.HttpResponse(
                #         json.dumps({
                #             "result": False,
                #             "msg": "Attempt to set negative score/games_played"
                #         }),
                #         mimetype="application/json"

                #     )
                # else:
                #     row['total_score'] += int(add_to_score)

            container.upsert_item(row)
            return func.HttpResponse(
                json.dumps({
                    "result": True,
                    "msg": "OK"
                }),
                mimetype="application/json",
                status_code=200
            )

        else:
            return func.HttpResponse(
                json.dumps({
                    "result": False,
                    "msg": "wrong password"
                }),
                mimetype="application/json"

            )

    return func.HttpResponse(
        json.dumps({
            "result": False,
            "msg": "user does not exist"
        }),
        mimetype="application/json"

    )
