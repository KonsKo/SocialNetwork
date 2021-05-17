from collector import Collector
import redis
import json
import pprint
import logging

logging.basicConfig(filename='example.log',
                    format='%(asctime)s %(message)s',
                    level=logging.DEBUG)

conn = redis.Redis()



data = conn.get('host_10.1.136.106_10364')

pprint.pprint(json.loads(data.decode('utf-8')))

