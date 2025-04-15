import json
from state import STATE_REQUEST_KEY
from request import *
from scenes import DEFAULT_SCENE, SCENES, Welcome
import ydb
import os

driver = ydb.Driver(
  endpoint=os.getenv('YDB_ENDPOINT'),
  database=os.getenv('YDB_DATABASE'),
  credentials=ydb.iam.MetadataUrlCredentials(),
)

# Wait for the driver to become active for requests.

driver.wait(fail_fast=True, timeout=5)

# Create the session pool instance to manage YDB sessions.
pool = ydb.QuerySessionPool(driver)

def handler(event, context):
    print('Incoming request: ' + json.dumps(event))
    #для сброса информации пользователя
    sc = Welcome()
    sc.make_respose('1')
    request = Request(event)
    current_scene_id = event.get('state').get(STATE_REQUEST_KEY, {}).get('scene')
    if current_scene_id is None:
        return DEFAULT_SCENE().reply(request, pool)
    current_scene = SCENES.get(current_scene_id, DEFAULT_SCENE)()
    next_scene = current_scene.move(request)
    if next_scene is not None:
        print(f'Moving from scene {current_scene.id()} to {next_scene.id()}')
        return next_scene.reply(request, pool)
    else:
        print(f'Failed to parse user request at scene {current_scene.id()}')
        return current_scene.fallback(request)
