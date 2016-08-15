# ansible-github-enterprise

Ansible playbook for GitHub Enterprise

## Roles

* `upgrade_ghe` - upgrade GHE to latest version (as determined by `ghe-update-check`)

## Configuration

`group_vars/all` is required, and contains the configuration for zenoss and vmware that will apply across all infrastructure types:

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
#  upgrade_package_url: https://github-enterprise.s3.amazonaws.com/esx/updates/github-enterprise-esx-2.7.1.pkg
  force_upgrade_to_latest: true
zenoss_uid: /zport/dmd/Devices/Server/Linux/devices/github-dev.someplace.edu
vm_name: changeme
```

* The `ghe.force_upgrade_to_latest` variable forces `ghe-update-check` to ignore the current release series in favor of the latest version available.
* The `ghe.upgrade_package_url` variable forces the playbook to download and run the specified upgrade package file. This option overrides `ghe.force_upgrade_to_latest` and should only be used to force the installation of a specific version.

## Upgrading GitHub Enterprise

```
ansible-playbook -i inventory/dev upgrade_ghe.yml
```
