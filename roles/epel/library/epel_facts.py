#!/usr/bin/python

# Copyright: (c) 2018, Terry Jones <terry.jones@example.org>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

ANSIBLE_METADATA = {
    'metadata_version': '1.0',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION = '''
---
module: epel_facts

short_description: This is my test module

version_added: "2.8"

description:
    - "Constructs information about the public EPEL for this machine."

options:
    distribution:
        description:
            - The Linux distribution of the target system.
        required: true
    major_version:
        description:
            - The major version of the Fedora based OS.
        required: true
    architecture:
        description:
            - The CPU architecture.
        required: true

author:
    - Ryan Kraus (@rmkraus)
'''

EXAMPLES = '''
# Pass in a message
- name: Test with a message
  my_test:
    name: hello world

# pass in a message and have changed true
- name: Test with a message and changed output
  my_test:
    name: hello world
    new: true

# fail the module
- name: Test failure of the module
  my_test:
    name: fail me
'''

RETURN = '''
has_epel:
    description: Whether an EPEL repo is available
    type: bool
    returned: always
url:
    description: URL to the EPEL repo
    type: str
    returned: always
has_gpg:
    description: Whether the GPG key URL is known to the module
    type: bool
    returned: always
gpg_url:
    description: URL to the GPG key for the Repo
    type: str
    returned: always
'''

RESULT_RPI = dict(
    has_epel = True,
    url = 'https://armv7.dev.centos.org/repodir/epel-pass-1/',
    has_gpg = False,
    gpg_url = '',
    changed = False
)

RESULT_67 = dict(
    has_epel = True,
    url = 'https://download.fedoraproject.org/pub/epel/{major_version}/{architecture}',
    has_gpg = True,
    gpg_url = 'https://download.fedoraproject.org/pub/epel/RPM-GPG-KEY-EPEL-{major_version}',
    changed = False
)

RESULT_8 = dict(
    has_epel = True,
    url = 'https://download.fedoraproject.org/pub/epel/{major_version}/Everything/{architecture}',
    has_gpg = True,
    gpg_url = 'https://download.fedoraproject.org/pub/epel/RPM-GPG-KEY-EPEL-{major_version}',
    changed = False
)

KNOWN_DISTROS = ['CentOS', 'RedHat']

from ansible.module_utils.basic import AnsibleModule

def run_module():
    # define inputs
    module_args = dict(
        distribution=dict(type='str', required=True),
        major_version=dict(type='int', required=True),
        architecture=dict(type='str', required=True)
    )

    # define outputs
    result = dict(
        has_epel=False,
        url='',
        has_gpg=False,
        gpg_url='',
        changed=False
    )

    # connect to Ansible
    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    # parse input args
    indata = dict(
        distribution = module.params['distribution'],
        architecture = module.params['architecture'],
        major_version = module.params['major_version'])

    # perform action
    if indata['distribution'] not in KNOWN_DISTROS:
        pass
    elif indata['major_version'] < 6:
        pass
    elif indata['architecture'] == 'armv7l':
        result = RESULT_RPI
    elif indata['major_version'] == 8:
        result = RESULT_8
    else:
        result = RESULT_67

    # format results
    for key in ['url', 'gpg_url']:
        result[key] = result[key].format(**indata)

    # exit
    module.exit_json(**result)

def main():
    run_module()

if __name__ == '__main__':
    main()
