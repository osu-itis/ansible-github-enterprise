#!/usr/bin/python
import pprint
import logging

pp = pprint.PrettyPrinter(indent=2)

DOCUMENTATION = '''
---
module: zenoss
short_description: Set production state on a device in Zenoss.
description:
  - The M(zenoss) module sets the production state on devices in Zenoss.
  - The I(zenoss_host), I(uid), and I(production_state) parameters are required.
author: Stacy Brock, @stacybrock
options:
  zenoss_host:
    description:
      - Hostname for the Zenoss server.
    required: true
  user:
    description:
      - Username to log into Zenoss.
    required: false
    default: null
  password:
    description:
      - Password to log into Zenoss.
    required: false
    default: null
  uid:
    description:
      - uid for the device in Zenoss.
    required: true
    default: null
  production_state:
    description:
      - Production state to set on the device.
    required: true
    choices: [ "production", "maintenance" ]
'''

def main():
    logging.basicConfig(filename='/tmp/ansible_zenoss_debug.log', level=logging.DEBUG)

    module = AnsibleModule(
        argument_spec=dict(
            zenoss_host=dict(required=True),
            user=dict(required=False),
            password=dict(required=False),
            uid=dict(required=True),
            production_state=dict(required=True, choices=['production', 'maintenance']),
        )
    )

    zenoss_host = module.params['zenoss_host']
    user = module.params['user']
    password = module.params['password']
    uid = module.params['uid']
    production_state = module.params['production_state']

    if not zenoss_host:
        module.fail_json(msg='zenoss_host not specified')

    if not (user or password):
        module.fail_json(msg='user or password not specified')

    ansible_zenoss = Zenoss(module, **module.params)
    (rc, out, changed) = ansible_zenoss.set_state()

    if rc != 0:
        module.fail_json(msg='failed', result=out)

    module.exit_json(msg='success', result=out, changed=changed)


class Zenoss(object):
    def __init__(self, module, **kwargs):
        self.module = module
        self.zenoss_host = kwargs['zenoss_host']
        self.user = kwargs['user']
        self.password = kwargs['password']
        self.uid = kwargs['uid']
        self.production_state = kwargs['production_state']

        self.auth = 'Basic {}'.format(
            base64.encodestring('{}:{}'.format(self.user, self.password)).replace('\n', '')
        )

        self.production_states = self._get_production_states()

    def _call_api(self, endpoint, action, method, data):
        api_url = 'https://' + self.zenoss_host + '/zport/dmd/' + endpoint
        headers = {
            'Authorization': self.auth,
            'Content-Type' : 'application/json',
        }
        request_data = {'action': action, 'method': method, 'data': [ data ], 'tid': '1'}
        data_json  = json.dumps(request_data)
        return fetch_url(self.module, api_url, headers=headers, data=data_json, method='POST')

    def _get_production_states(self):
        response, info = self._call_api('device_router', 'DeviceRouter', 'getProductionStates', '')
        if info['status'] != 200:
            self.module.fail_json(msg='failed to retrieve production states: {}'.format(info['msg']))

        try:
            json_out = json.loads(response.read())
        except:
            json_out = ""

        if 'result' not in json_out:
            self.module.fail_json(msg='failed to retrieve production states: bad response from server, check hostname, user, and password')
        if json_out['result']['success'] != True:
            self.module.fail_json(msg='failed to retrieve production states: {}'.format(json_out['result']['msg']))

        states = {}
        for item in json_out['result']['data']:
            states[item['name'].lower()] = item['value']

        return states

    def set_state(self):
        statecode = self.production_states[self.production_state]

        response, info = self._call_api('device_router', 'DeviceRouter', 'setInfo', {'uid': self.uid, 'productionState': statecode})
        if info['status'] != 200:
            self.module.fail_json(msg='failed to set production state: {}'.format(info['msg']))

        try:
            json_out = json.loads(response.read())
        except:
            json_out = ""

        if json_out['result']['success'] != True:
            self.module.fail_json(msg='failed to set production state: {}'.format(json_out['result']['msg']))

        return False, json_out, True


from ansible.module_utils.basic import *
from ansible.module_utils.urls import *

if __name__ == '__main__':
    main()
