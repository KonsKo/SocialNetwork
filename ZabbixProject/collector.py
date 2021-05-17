import json
import re
import requests
import redis
import sys
from typing import Dict, List
from types import SimpleNamespace

from zapi_logger import zapi_logger


def zapi_auth():
    config = Loader().config
    url_zabbix = config.ZABBIX.URL
    login = config.ZABBIX.LOGIN
    password = config.ZABBIX.PASSWORD
    headers = {"Content-Type": "application/json"}
    data = {
        "jsonrpc": "2.0",
        "method": "user.login",
        "params": {
            "user": f"{login}",
            "password": f"{password}"
        },
        "id": 1,
        "auth": None
    }
    try:
        response = requests.post(url_zabbix, data=json.dumps(data), headers=headers)
        token = response.json()['result']
        return token
    except KeyError:
        zapi_logger.exception('message')


class Loader:

    @property
    def config(self) -> SimpleNamespace:
        try:
            with open('config.json', 'r') as config_file:
                data = json.load(config_file, object_hook=lambda d: SimpleNamespace(**d))
            return data
        except FileNotFoundError:
            zapi_logger.exception('message')
            sys.exit(1)


class BaseCollector:

    def __init__(self):
        self.config = Loader().config
        self.headers = {"Content-Type": "application/json"}
        self.client = redis.Redis(host=self.config.REDIS.HOST,
                                  port=self.config.REDIS.PORT,
                                  socket_timeout=self.config.REDIS.SOCKET_TIMEOUT
                                  )
        self.url_zabbix = self.config.ZABBIX.URL
        self.ip_zabbix = re.search('[0-9.]+', self.url_zabbix).group()


class Collector(BaseCollector):

    def __init__(self, data: Dict):
        super().__init__()
        self.token = zapi_auth()
        self.data = {**data, **{"auth": self.token}}
        self.elements = []

    def collect(self) -> List:
        if not self.token:
            zapi_logger.info('There is no token')
        else:
            elements = requests.post(url=self.url_zabbix,
                                     data=json.dumps(self.data),
                                     headers=self.headers
                                     )
            self.elements = elements.json()['result']
            return self.elements

    def add_problem(self, search_id, insert_problems) -> None:
        for element in self.elements:
            if element['hostid'] == search_id:
                try:
                    current_problems = element["problems"]
                except KeyError:
                    element["problems"] = []
                    current_problems = element["problems"]
                current_problems.append(insert_problems)
                element['problems'] = current_problems

    def to_redis(self) -> None:
        for element in self.elements:
            element_id = element.get('hostid')
            element_key = f"host_{self.ip_zabbix}_{element_id}"
            try:
                self.client.set(element_key,
                                json.dumps(element)
                                )
            except redis.exceptions.TimeoutError:
                zapi_logger.exception('message')
                sys.exit(1)
