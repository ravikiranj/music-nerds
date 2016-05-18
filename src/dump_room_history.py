#!/usr/bin/env python
import requests
import simplejson
import datetime
import logging
import json

from dateutil.parser import parse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("dump_room_history")


def get_res(url, until_date, max_results, op_filename):
    if op_filename is None:
        raise Exception("Output file cannot be None")
    params = {"auth_token": AUTH_TOKEN}
    if until_date is not None:
        params["date"] = until_date
    if max_results is not None:
        params["max-results"] = max_results

    r = requests.get(url, params=params)
    json_data = r.json()

    if r.status_code != 200:
        logger.info("Encountered status_code = %d, most probably we fetched the entire room history.", r.status_code)
        logger.info("Error Message = %s, Params = %s", json_data, simplejson.dumps(params))
        return None

    with open(op_filename, "w") as op:
        simplejson.dump(json_data, op, indent=4, sort_keys=True)
        logger.info("Wrote response to %s", op_filename)

    if "items" in json_data and len(json_data["items"]) > 1 and "date" in json_data["items"][0]:
        return json_data["items"][0]["date"]
    else:
        return None


def get_fixed_next_date(date_str):
    if date_str is not None:
        d = parse(date_str) - datetime.timedelta(days=1)
    else:
        d = None
    return d

def get_json_config():
    with open("config.json") as ip:
        return json.load(ip)

config = get_json_config()
AUTH_TOKEN = config["hipchat_auth_token"]
# Music Nerds API Id
room_id = config["music_room_api_id"]
base_url = "https://" + config["hipchat_server"] + "/v2/room/%d/history" % (room_id)
today = datetime.datetime.utcnow().isoformat()
max_res = 1000

current_result = 0
next_date = today
while next_date is not None:
    op_file = "../data/raw/room_history_%02d.json" % current_result
    if current_result == 0:
        next_date_str = get_res(base_url, str(next_date), max_res, op_file)
        next_date = get_fixed_next_date(next_date_str)
    else:
        next_date_str = get_res(base_url, str(next_date), max_res, op_file)
        next_date = get_fixed_next_date(next_date_str)
    current_result += 1
