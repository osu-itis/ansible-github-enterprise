# ansible-github-enterprise

Ansible playbook for GitHub Enterprise

## Roles

* `upgrade_ghe` - upgrade GHE to latest version (as determined by `ghe-update-check`)

## Configuration

Example `group_vars/all`:

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
  force_upgrade_to_latest: true
zenoss_uid: /zport/dmd/Devices/Server/Linux/devices/github-dev.someplace.edu
vm_name: changeme
```

* The `ghe.force_upgrade_to_latest` variable forces `ghe-update-check` to ignore the current release series in favor of the latest version available.

## Upgrading GitHub Enterprise

```
ansible-playbook -i inventory/dev upgrade_ghe.yml
```
