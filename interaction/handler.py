import json
import os

from request import *
from scenes import DEFAULT_SCENE, SCENES, Fallback
from state import STATE_REQUEST_KEY

import ydb

driver = ydb.Driver(
    endpoint=os.getenv("YDB_ENDPOINT"),
    database=os.getenv("YDB_DATABASE"),
    credentials=ydb.iam.MetadataUrlCredentials(),
)

# Wait for the driver to become active for requests.

driver.wait(fail_fast=True, timeout=5)

# Create the session pool instance to manage YDB sessions.
pool = ydb.QuerySessionPool(driver)


def handler(event, context):
    try:
        print("Incoming request: " + json.dumps(event))
        request = Request(event)

        current_scene_id = (
            event.get("state", {}).get(STATE_REQUEST_KEY, {}).get("scene")
        )
        if current_scene_id is None:
            return DEFAULT_SCENE().reply(request, pool)

        current_scene = SCENES.get(current_scene_id, DEFAULT_SCENE)()
        next_scene = current_scene.move(request)
        if next_scene is not None:
            print(f"Moving from scene {current_scene.id()} to {next_scene.id()}")
        else:
            next_scene = Fallback()
        return next_scene.reply(request, pool)

    except Exception as e:
        print(f"Error occurred: {str(e)}")
        import traceback
        traceback.print_exc()
        next_scene = Fallback()
        return next_scene.reply(request, pool)
