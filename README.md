# ansible-github-enterprise

Ansible playbook for GitHub Enterprise

This playbook assumes you are running GitHub Enterprise under SSL.

## Roles

* `upgrade_ghe` - upgrade GHE to latest version (as determined by `ghe-update-check`)

## Configuration

For `dev`, `stage`, `prod`, etc., create an inventory and variable file for each infrastructure type.

Example `inventory/dev`:

```
[dev]
github-dev.someplace.edu:122
```

Example `group_vars/dev`:

```
---
ghe:
  sign_in_check_string: Sign in to your account
  #upgrade_package_url: https://github-enterprise.s3.amazonaws.com/esx/updates/github-enterprise-esx-2.7.1.pkg
  #force_upgrade_to_latest: true
  #validate_cert: true
zenoss_uid: /zport/dmd/Devices/Server/Linux/devices/github-dev.someplace.edu
vm_name: changeme
```

* `ghe.sign_in_check_string` - The string to search for when checking if the application has successfully come back up after an upgrade. For deployments using the default GitHub authentication, the value should be 'Sign in to your account' as shown in the example.
* `ghe.force_upgrade_to_latest` (optional) - Force `ghe-update-check` to ignore the current release series in favor of the latest version available.
* `ghe.upgrade_package_url` (optional) - Force the playbook to download and run the specified upgrade package file. Hotpatch package files are also supported. This option overrides `ghe.force_upgrade_to_latest` and should only be used to install a specific version.
* `ghe.validate_cert` (optional) - Set to `false` to skip SSL certificate validation when checking if the application has successfully come back up after an upgrade. Not recommended unless you really need this!
* `zenoss_uid` (optional) - Zenoss device uid for managing maintenance state
* `vm_name` (optional) - VMware VM name that is running GitHub Enterprise

If `zenoss_uid` and `vm_name` config options are defined, `group_vars/all` must contain the configuration for Zenoss and VMware that will apply across all infrastructure types:

```
---
zenoss:
    hostname: zenoss.someplace.edu
    user: changeme
    password: changeme
vmware:
    hostname: vcenter.someplace.edu
    user: changeme
    password: changeme
    skip_certcheck: false
```

## Upgrading GitHub Enterprise

```
ansible-playbook -i inventory/dev upgrade_ghe.yml
```
