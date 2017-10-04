import promote
from schema import Schema  # https://pypi.python.org/pypi/schema

import os
from helpers import tempdesc
from helpers import get_weather

# instanciate the Promote class with our API information
USERNAME = "colin"
API_KEY = "789asdf879h789a79f79sf79s"
PROMOTE_URL = "https://sandbox.c.yhat.com/"
DARKSKY_API_KEY = os.environ['DARKSKY_API_KEY'] # get a darksky api key: https://darksky.net/dev

p = promote.Promote(USERNAME, API_KEY, PROMOTE_URL)

# validate that we only process data that has ints and floats
@promote.validate_json(Schema({'lat': str, 'lon': str}))
def promoteModel(data):
    lat = data.get('lat')
    lon = data.get('lon')
    temp = get_weather.request_weather(DARKSKY_API_KEY, lat, lon)
    desc = tempdesc.lookup(temp)
    return {"tempature": temp, "feels": desc}

# some test data
TESTDATA = {'lat':'37', 'lon':'-122'}
print(promoteModel(TESTDATA))

# name and deploy our model
# p.deploy("UserDBLookup", promoteModel, TESTDATA, confirm=True, dry_run=True, verbose=0)

# once our model is deployed and online, we can send data and recieve predictions
# p.predict("UserDBLookup", TESTDATA)

# example result
# {
#     "tempature": 73.67, 
#     "feels": "Warm"
# }