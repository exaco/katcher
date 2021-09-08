#!/usr/bin/env python

"""An exporter to fetch a fields value and count it for prometheus."""

from time import sleep

import prometheus_client as prom

from broker import KafkaHandler
from config import Config


service = Config().service
counter_name = Config().counter_name
header_field = Config().header_field
counter = prom.Counter(
    "{}_{}".format(service, counter_name),
    "The {}'s {} counter".format(service, header_field),
    ["service", header_field, "topic"]
)
exposed_port = Config().port


def export_header_field_value(headers, header_field=header_field):
    value = None
    try:
        for item in headers:
            if item[0] == header_field:
                value = item[1]
                break
    except Exception as e:
        print(
            "ERROR: Error in looping on headers. Ensure topics are currect",
            e
        )
    return value


if __name__ == "__main__":
    prom.start_http_server(exposed_port)
    consumer = KafkaHandler()
    print("Daemon started successfully on port {} ...".format(exposed_port))
    for message in consumer.consume_loop():
        try:
            headers = message.headers()
            topic = message.topic()
            if headers != None:
                api_index_id = export_header_field_value(
                    headers,
                    header_field
                )
                try:
                    api_index_id = int(api_index_id)
                except TypeError as e:
                    print("ERROR: invalid header value")
                    continue
                finally:
                    consumer.try_commit()
                counter.labels(service, api_index_id, topic).inc()
        except Exception as e:
            print("ERROR: ", e)
