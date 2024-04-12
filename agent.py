from pipeless_agents_sdk.cloud import data_stream

print(f"Ready! Add a pipeline to start receiving data!")
for payload in data_stream:
    print(f"New data received: {payload.value}")

