from pipeless_agents_sdk.cloud import data_stream

for payload in data_stream:
    print(f"New data received: {payload.value}")

