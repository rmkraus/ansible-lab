#!/usr/bin/env python
""" Ansible module: lock """
# Copyright: (c) 2019, Ryan Kraus (rkraus@redhat.com)
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

import os
import sys
import tokenize
from ansible.module_utils.basic import AnsibleModule

ANSIBLE_METADATA = {
    'metadata_version': '1.0',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION = '''
---
module: lock   

short_description: Provides a locking mechanism to Ansible code

version_added: "2.8"

description:
    - "Provides a locking mechanism for Ansible."
    - "Locks are target specific unless delegated to the localhost."
    - "This role will fail 

options:
    name:
        description:
            - The name of the lock.
            - Must not begin with numbers.
            - Must not contain special characters except and under score (_).
            - Must not contain spaces.
            - Names are case sensitive only when the target system's file system
              is case sensitive.
        required: true
    state:
        description:
            - The desired state for the lock.
        required: false
        default: acquired
        choices:
          - acquired
          - released
    permanent:
        description:
            - Should the lock be set permanently or ephemerally?
            - Permanent locks require write access to "/var/cache/ansible-lock".
            - Ephemeral locks are stored in /tmp/ansible-lock and last as long 
              as that directory.
            - This only changes the behavior when setting the lock as permenent 
              and ephemeral locks exist in the same namespace.
        required: false
        default: False
        choices: 
            - True
            - False

author:
    - Ryan Kraus (@rmkraus)
'''

EXAMPLES = '''
# Acquire a lock, fail if the lock is not available
- name: Acquire a lock
  lock:
    name: hello_world

# Acquire a lock permanently
- name: Acquire a lock
  lock:
    name: hello_world
    state: acquired
    permanent: True

# Release a lock
- name: Release a lock
  lock:
    name: hello_world
    state: released

# Block until a lock is available
- name: Block until lock
  lock:
    name: hello_world
    state: acquired
  register: my_lock
  until: my_lock is success
  retries: 1000
  delay: 10
'''

RETURN = '''
'''

_EPEHMERAL_DIR = "/tmp/ansible-lock"
_PERMANENT_DIR = "/var/cache/ansible-lock"


def _validname(ident):
    '''Check if string value is a valid lock name.'''
    if not isinstance(ident, str):
        return False

    readline = lambda g=(lambda: (yield ident))(): next(g)
    tokens = list(tokenize.generate_tokens(readline))

    # First is NAME, identifier.
    if tokens[0][0] != tokenize.NAME:
        return False

    # Name should span all the string, so there would be no whitespace.
    if ident != tokens[0][1]:
        return False

    return True


def _release(name):
    '''Release a lock if it exists.'''
    lock = _find_lock(name)

    if not lock:
        return (True, '')

    os.remove(lock)
    return (True, '')


def _acquire(name, permanent):
    '''Acquire a lock.'''
    lock_exists = bool(_find_lock(name))
    if lock_exists:
        return (False, 'Lock already exists.')

    if permanent:
        lock_dir = _PERMANENT_DIR
        lock_mode = 0o0
    else:
        lock_dir = _EPEHMERAL_DIR
        lock_mode = 0o2777
    lock_path = os.path.join(lock_dir, name)

    if not os.path.exists(lock_dir):
        os.makedirs(lock_dir)
        if lock_mode:
            os.chmod(lock_dir, lock_mode)

    open(lock_path, 'a').close()
    if lock_mode:
        os.chmod(lock_path, lock_mode)

    return (True, '')


def _find_lock(name):
    '''Locate a lock.'''
    for search_dir in [_EPEHMERAL_DIR, _PERMANENT_DIR]:
        search_path = os.path.join(search_dir, name)
        if os.path.exists(search_path):
            return search_path
    return ''


def main():
    """Main function executed by Ansible."""
    # define inputs
    module_args = dict(
        name=dict(type='str', required=True),
        state=dict(type='str', required=False, default="acquired"),
        permanent=dict(type='bool', required=False, default=False)
    )

    # connect to Ansible
    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    # exit if check mode
    if module.check_mode:
        module.exit_json(changed=False)

    # parse input args
    indata = dict(
        name=module.params['name'],
        state=module.params['state'],
        permanent=module.params['permanent'])
    if not _validname(indata['name']):
        module.fail_json(msg='The lock name is not valid.', changed=False)

    # perform action
    try:
        if indata['state'] == 'acquired':
            (success, msg) = _acquire(indata['name'], indata['permanent'])
        elif indata['state'] == 'released':
            (success, msg) = _release(indata['name'])
        else:
            success = False
            msg = 'Unrecognized value for state. ' + \
                'State can be acquired or released.'
    except (OSError, IOError) as err:
        success = False
        msg = str(err.strerror)

    # exit
    if success:
        module.exit_json(changed=True)
    else:
        module.fail_json(msg=msg, changed=False)


if __name__ == '__main__':
    main()
