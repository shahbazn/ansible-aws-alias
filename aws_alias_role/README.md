aws-alias
===

## What

This role was developed to manage AWS account aliases. It can set, update or remove account alias from
the given AWS account. 


## Usage

```
Module Name: iam_alias
Parameters:
  aws_account_alias: If set, changes AWS account alias name.
                     If this parameter is not set, role does
                     nothing
  aws_account_state: If set to absent, removes account alias.
                     Accepts 'present', 'absent', defaults to 'present'
  aws_access_key   : AWS account access key ID, defaults to AWS_ACCESS_KEY_ID
                     environment variable
  aws_secret_key   : AWS account access key secret, defaults to AWS_SECRET_ACCESS_KEY
                     environment variable
```

## Example Role

```
- name: Ensure AWS alias name
  iam_alias:
    aws_account_alias: "{{ aws_account_alias }}"
    aws_account_state: "{{ aws_account_state }}"
    aws_access_key: "{{ aws_access_key}}"
    aws_secret_key: "{{ aws_secret_key}}"
  register: aws_alias_status
```

## Module Dependencies

Modules depends on the following python libraries
  - boto3==1.4.4
  - botocore==1.5.48

## Testing
### Unit Test Requirements
Unit testing Depends on following python modules
  - mock==2.0.0
  - nose==1.3.7

### Integeration Test Requirements

 - docker CE
 - ruby 2.3
 - ruby bundler
 - bundle install the aws_alias_role Gemfile

CAVEAT: If the alises being used in integration tests get consumed before
        running tests the tests will fail. 

### Running Tests
- install docker CE
- setup environment
```
sudo apt-add-repository ppa:brightbox/ruby-ng
sudo apt-get update
sudo apt-get install ruby2.3 ruby2.3-dev
sudo gem install bundler
```
- Run test script
```
./run_tests.sh -h

Usage:
./run_tests.sh
    -h --help
    --access-key=AWS_ACCESS_KEY_ID
    --access-secret=AWS_SECRET_ACCESS_KEY
```

### Test coverage
 - Tests cover Ansible 2.0, 2.1 and 2.2