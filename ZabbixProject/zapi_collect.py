import json

from collector import Collector


with open('zapi_templates.json', 'r') as template_file:
    zapi_templates = json.load(template_file)


def processing_collection():
    hosts = Collector(data=zapi_templates.get('data_host'))
    hosts.collect()
    problems = Collector(data=zapi_templates.get('data_problems'))

    for problem in problems.collect():
        object_id = problem['objectid']  # trigger id
        trigger_data = zapi_templates.get('data_triggers')
        trigger_data['params']['triggerids'] = object_id
        trigger = Collector(data=trigger_data).collect()[0]
        if trigger['hosts'][0]['available'] != '2':  # '2' - host is unavailable
            host_id = trigger['hosts'][0]['hostid']
            del trigger['hosts']
            problem['cur_trigger'] = trigger
            hosts.add_problem(host_id, problem)

    hosts.to_redis()


if __name__ == '__main__':
    processing_collection()
