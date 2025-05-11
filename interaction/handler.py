import json
from state import STATE_REQUEST_KEY
from request import *
from scenes import DEFAULT_SCENE, SCENES, Fallback
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
    try:
        print('Incoming request: ' + json.dumps(event))
        # для сброса информации пользователя
        request = Request(event)
        
        # Получаем текущую сцену или используем сцену по умолчанию
        current_scene_id = event.get('state', {}).get(STATE_REQUEST_KEY, {}).get('scene')
        if current_scene_id is None:
            return DEFAULT_SCENE().reply(request, pool)
            
        current_scene = SCENES.get(current_scene_id, DEFAULT_SCENE)()
        
        # Пытаемся обработать переход между сценами
        next_scene = current_scene.move(request)
        if next_scene is not None:
            print(f'Moving from scene {current_scene.id()} to {next_scene.id()}')
            #next_scene.reply(request, pool)
        else:
            #print(f'Failed to parse user request at scene {current_scene.id()}')
            #return current_scene.fallback(request)
            next_scene = Fallback()
        return next_scene.reply(request, pool)
            
    except Exception as e:
        print(f'Error occurred: {str(e)}')
        # Логируем полный traceback для отладки
        import traceback
        traceback.print_exc()
        
        # Возвращаем fallback текущей сцены или сцены по умолчанию
        next_scene = Fallback()
        #fallback_scene = current_scene.fallback(request) if 'current_scene' in locals() else DEFAULT_SCENE().fallback(request)
        #return fallback_scene
        return next_scene.reply(request, pool)
