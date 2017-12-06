import promote
from schema import Schema, And

# schema is optional https://pypi.python.org/pypi/schema
@promote.validate_json(Schema({'name': And(str, lambda s: len(s) > 1)}))
def helloWorld(data):
    return {'response': 'Hello ' + data['name'] + '!'}

USERNAME = 'ross'
API_KEY = '2dcf2d39-0d4a-4d4b-b79d-7b7033e0532f'
PROMOTE_URL = "http://promote.x.yhat.com/"

p = promote.Promote(USERNAME, API_KEY, PROMOTE_URL)

# test data
TESTDATA = {'name': 'austin'}

# test model locally
print(helloWorld(TESTDATA))

# 1. test that TESTDATA is valid json
# 2. THERE IS test data, run helloWorld(TESTDATA) before deployment
p.deploy("HelloModel", helloWorld, TESTDATA, confirm=True, dry_run=False, verbose=1)