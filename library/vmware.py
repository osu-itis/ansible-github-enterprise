#!/usr/bin/python
import pprint
import logging
pp = pprint.PrettyPrinter(indent=2)

import ssl
import atexit

try:
    from pyVim.connect import SmartConnect, Disconnect
    from pyVmomi import vim, vmodl
    HAS_PYVMOMI = True
except ImportError:
    HAS_PYVMOMI = False


def main():
    logging.basicConfig(filename='/tmp/ansible_vmware_debug.log', level=logging.DEBUG)

    module = AnsibleModule(
        argument_spec=dict(
            vsphere = dict(type='dict', required=True),
            guest = dict(type='dict'),
            snapshot = dict(type='dict'),
        )
    )

    if not HAS_PYVMOMI:
        module.fail_json(msg='pyvmomi is required')

    vsphere = module.params['vsphere']
    guest = module.params['guest']
    snapshot = module.params['snapshot']

    # validate parameters
    if 'host' not in vsphere:
        module.fail_json(msg='vsphere host is not specified')
    if 'user' not in vsphere or 'password' not in vsphere:
        module.fail_json(msg='vsphere user or password not specified')

    if guest is not None:
        if 'name' not in guest:
            module.fail_json(msg='guest name is missing')

    if snapshot is not None:
        if 'action' not in snapshot:
            module.fail_json(msg='snapshot action is missing')
        if snapshot['action'] not in ['create']:
            module.fail_json(msg='snapshot action is invalid, choices are [ create ]')
        if 'name' not in snapshot:
            module.fail_json(msg='snapshot name is missing')

    # DO STUFF HERE
    vmware = VMware(module, **module.params)

    if snapshot is not None:
        if snapshot['action'] == 'create':
            (rc, out, changed) = vmware.create_snapshot()

    if rc != 0:
        module.fail_json(msg='failed', result=out)

    module.exit_json(msg='success', result=out, changed=changed)


class VMware(object):
    def __init__(self, module, **kwargs):
        self.module = module
        self.vsphere = kwargs['vsphere']
        self.guest = kwargs['guest']
        self.snapshot = kwargs['snapshot']

        # set some sane defaults for missing optional parameters
        if 'port' not in self.vsphere:
            logging.debug('no port defined, setting 443 as default')
            self.vsphere['port'] = 443
        if 'skip_certcheck' not in self.vsphere:
            logging.debug('skip_certcheck not defined, setting false as default')
            self.vsphere['skip_certcheck'] = False

        if 'description' not in self.snapshot:
            logging.debug('description not defined, setting default')
            self.snapshot['description'] = 'created by ansible'
        if 'include_memory' not in self.snapshot:
            logging.debug('include_memory not defined, setting false as default')
            self.snapshot['include_memory'] = False

        # connect to vSphere
        if self.vsphere['skip_certcheck']:
            context = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
            context.verify_mode = ssl.CERT_NONE

        try:
            if self.vsphere['skip_certcheck']:
                self.si = SmartConnect(host=self.vsphere['host'], user=self.vsphere['user'], pwd=self.vsphere['password'], port=self.vsphere['port'], sslContext=context)
            else:
                self.si = SmartConnect(host=self.vsphere['host'], user=self.vsphere['user'], pwd=self.vsphere['password'], port=self.vsphere['port'])
        except:
            self.module.fail_json(msg='could not connect to host {}'.format(self.vsphere['host']))

        atexit.register(Disconnect, self.si)

        # find vm by name
        content = self.si.content
        obj_view = content.viewManager.CreateContainerView(content.rootFolder, [vim.VirtualMachine], True)
        vms = obj_view.view
        obj_view.Destroy()

        vm_found = False
        for vm in vms:
            if vm.name == self.guest['name']:
                vm_found = True
                self.vm = vm

        if not vm_found:
            self.module.fail_json(msg='could not find vm {}'.format(self.guest['name']))


    def _wait_task(self, task):
        while (task.info.state != vim.TaskInfo.State.success and task.info.state != vim.TaskInfo.State.error):
            time.sleep(2)

        failed = False
        if task.info.state == vim.TaskInfo.State.success:
            failed = False
            outmsg = '{} task completed successfully'.format(task.info.task)
        else:
            failed = True
            if task.info.error:
                outmsg = '{} task failed: {}'.format(task.info.task, task.info.error.msg)
            else:
                outmsg = '{} task failed: error is unknown, state is {}'.format(task.info.task, task.info.state)

        return failed, outmsg, task


    def create_snapshot(self):
        task = self.vm.CreateSnapshot(name=self.snapshot['name'], description=self.snapshot['description'], memory=self.snapshot['include_memory'], quiesce=False)
        failed, out, __ = self._wait_task(task)

        return failed, dict(msg='create snapshot {}'.format(out)), True


from ansible.module_utils.basic import *
from ansible.module_utils.urls import *

if __name__ == '__main__':
    main()
