import os
import ydb
import ydb.iam
import registration_ydb as r

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

    r.registration_user(['Алексей', 'Вбивалкин', 'Петрович'], [], pool, is_student=False)
    return {
        'statusCode': 200,
        'body': 'a',
    }
