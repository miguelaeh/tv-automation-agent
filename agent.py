from pipeless_agents_sdk.cloud import data_stream
import time
import requests
import os
import json

hass_webhook_url = os.getenv("HASS_WEBHOOK_URL")
seconds_without_person = os.getenv("SECONDS_WITHOUT_PERSON")
person_conf = os.getenv("PERSON_CONFIDENCE_THR")
tv_conf = os.getenv("TV_CONFIDENCE_THR")

if not hass_webhook_url:
    raise "Missing HASS_WEBHOOK_URL env var. Please add it to the agent configuration"
if not seconds_without_person:
    raise "Missing SECONDS_WITHOUT_PERSON env var. Please add it to the agent configuration"
if not person_conf:
    person_conf = 0.65
    print(f"Warning: PERSON_CONFIDENCE_THR env var not specified. Defaulting to {person_conf}. You can adjust the confidence by providing the env var in the agent configuration\n")
if not tv_conf:
    tv_conf = 0.7
    print(f"Warning: TV_CONFIDENCE_THR env var not specified. Defaulting to {tv_conf}. You can adjust the confidence by providing the env var in the agent configuration\n")

print(f"READY! Add a pipeline using Home Assistant as video source to start automating your home with vision!")

tv_on = True # Whether the TV is on (true) or off (false)
prev_person = False # Whether there is a person
person_leaves_at = 0 # time at which the person leaves.

def person_present(data):
    for item in data:
        class_name = item.get('class_name', None)
        score = item.get('score', None)
        if class_name == 'person' and score > person_conf:
            return True
    return False

def is_tv_on(data):
    for item in data:
        class_name = item.get('class_name', None)
        score = item.get('score', None)
        if class_name == 'TV on' and score > tv_conf:
            return True
    return False

def turn_off_tv():
    # If there is no person in 30 seconds, Send webhook to turn off TV.
    response = requests.get(hass_webhook_url)
    if response.status_code == 200:
        print(f"TV turned OFF since there no one watching in more than {seconds_without_person} seconds")
    else:
        print("ERROR: turning off TV. Webhook request returned: {response.status_code} status")

for payload in data_stream:
    payload = json.loads(payload.value)
    current_person = person_present(payload)
    if not current_person and prev_person:
        person_leaves_at = time.time()
        prev_person = False
    elif not current_person and not prev_person and is_tv_on(payload):
        elapsed = time.time() - person_leaves_at
        if elapsed > seconds_without_person:
            turn_off_tv()
    else:
        prev_person = True
