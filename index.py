import os
import ydb
import ydb.iam
import registration_ydb as r
import input_output_lesson_ydb as ioy
# Create driver in global space.
driver = ydb.Driver(
  endpoint=os.getenv('YDB_ENDPOINT'),
  database=os.getenv('YDB_DATABASE'),
  credentials=ydb.iam.MetadataUrlCredentials(),
)

# Wait for the driver to become active for requests.

driver.wait(fail_fast=True, timeout=5)

# Create the session pool instance to manage YDB sessions.
pool = ydb.QuerySessionPool(driver)

def execute_query(pool):
  # Create the transaction and execute query.
  res = pool.execute_with_retries('select * from Group;')
  return res

def handler(event, context):
  # Execute query with the retry_operation helper.
  #работает
  #r.registration_user(['Алексей', 'Вбивалкин', 'Петрович'], [], pool, is_student=False)
  #работает
  #ioy.insert_lesson(['Вася', 'Иванов', 'Евпатиевич', 1], ['Матан', 'семинар', 'Родионова',
                                              #'303', 1, '12:00', 'вторник', True, '12.04.2004', 1], True, True, pool)
  #работает
  #ioy.insert_lesson(['Вася', 'Иванов', 'Евпатиевич', 1], ['Матан', 'семинар', 'Родионова',
  #                                            '303', 1, '12:00', 'вторник', True, '12.04.2004', 1], True, False, pool)
  #работает
  #ioy.insert_lesson(['Алексей', 'Вбивалкин', 'Петрович'], ['Матан', 'семинар', 'Родионова',
  #                                            '303', 1, '12:00', 'вторник', True, '12.04.2004', 1], False, True, pool)
  #работает
  #ioy.insert_lesson(['Алексей', 'Вбивалкин', 'Петрович'], ['Матан', 'семинар', 'Родионова',
  #                                            '303', 1, '12:00', 'вторник', True, '12.04.2004', 1], False, False, pool)
  return {
    'statusCode': 200,
    'body': 'a',
  }
