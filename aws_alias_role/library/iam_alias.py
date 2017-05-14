#!/usr/bin/python

DOCUMENTATION = '''
---
module: iam_alias
short_description: Manage IAM users, groups, roles and keys
description:
     - Allows for the management of IAM users, user API keys, groups, roles.
version_added: "2.2.1.0"
options:
  aws_account_alias:
    description:
      - If set, changes AWS account alias name. If this parameter is not set, role does nothing.
  aws_account_state:
    description:
      - Changes AWS account alias name if set to present. If set to absent, removes account alias.
    default: present
    choices: [ "preset", "absent"]

  access_key_id:
    description:
      - Access key for the AWS account to which you want to add the account alias.
  aws_secret_key:
    description:
      - Secrete Key for the AWS account to which you want to add the account alias
author:
    - "Shahbaz Nazir (@shahbazn)"

'''

EXAMPLES = '''
# Basic alias creation example
tasks:
- name: Create AWS account alias
  iam_alias:
    aws_account_alias: "{{ aws_account_alias }}" 
    aws_account_state: present
    aws_access_key: "{{ aws_access_key_id }}"
    aws_secret_key: "{{ aws_secret_key }}"
  register: aws_alias_status
'''

try:
    import boto3
    HAS_BOTO = True
except ImportError:
    HAS_BOTO = False


def main():
    argument_spec = dict(
    	aws_account_alias=dict(default=None, required=False),
        aws_account_state=dict(
            default=None, required=True, choices=['present', 'absent']),
        aws_access_key=dict(default=None, required=False),
        aws_secret_key=dict(default=None, required=False),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        mutually_exclusive=[['trust_policy', 'trust_policy_filepath']],
    )

    if not HAS_BOTO:
        module.fail_json(msg='This module requires boto3, please install it')

    aws_account_alias = module.params.get('aws_account_alias')
    aws_account_state = module.params.get('aws_account_state').lower()
    aws_access_key = module.params.get('aws_access_key')
    aws_secret_key = module.params.get('aws_secret_key')


from ansible.module_utils.basic import *

if __name__ == '__main__':
    main()