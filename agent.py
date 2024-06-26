from pipeless_agents_sdk.cloud import data_stream
import time
import requests
import os

hass_webhook_url = os.getenv("HASS_WEBHOOK_URL")
seconds_without_person_str = os.getenv("SECONDS_WITHOUT_PERSON")
person_conf_str = os.getenv("PERSON_CONFIDENCE_THR")
tv_conf_str = os.getenv("TV_CONFIDENCE_THR")

if not hass_webhook_url:
    raise "Missing HASS_WEBHOOK_URL env var. Please add it to the agent configuration"
if seconds_without_person_str:
    seconds_without_person = float(seconds_without_person_str)
else:
    raise "Missing SECONDS_WITHOUT_PERSON env var. Please add it to the agent configuration"
if person_conf_str:
    person_conf = float(person_conf_str)
else:
    person_conf = 0.65
    print(f"Warning: PERSON_CONFIDENCE_THR env var not specified. Defaulting to {person_conf}. You can adjust the confidence by providing the env var in the agent configuration\n")
if tv_conf_str:
    tv_conf = float(tv_conf_str)
else:
    tv_conf = 0.7
    print(f"Warning: TV_CONFIDENCE_THR env var not specified. Defaulting to {tv_conf}. You can adjust the confidence by providing the env var in the agent configuration\n")

print(f"READY! Add a pipeline using Home Assistant as video source to start automating your home with vision!")

tv_on = True # Whether the TV is on (true) or off (false)
prev_person = False # Whether there is a person
person_leaves_at = 0 # time at which the person leaves.

def person_present(data):
    for item in data:
        print(item)
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
    print("Tunrning off TV!")
    # If there is no person in 30 seconds, Send webhook to turn off TV.
    try:
        response = requests.post(hass_webhook_url, timeout=2)
        if response.status_code == 200:
            print(f"TV turned OFF since there no one watching in more than {seconds_without_person} seconds")
        else:
            print(f"ERROR: turning off TV. Webhook request returned: {response.status_code} status")
    except Exception as e:
        print(f"ERROR: failed to call webhook endpoint: {e}")

for payload in data_stream:
    data = payload.value["data"]
    print(f"Got data: {data}")
    current_person = person_present(data)
    if not current_person and prev_person:
        person_leaves_at = time.time()
        prev_person = False
    elif not current_person and not prev_person and is_tv_on(data):
        elapsed = time.time() - person_leaves_at
        if elapsed > seconds_without_person:
            turn_off_tv()
    elif current_person:
        prev_person = True
