#!/bin/bash
set -e

echo "Setting up ansible virtual environments"

SETUP_VERSION="v0.0.5"

## Install Ansible 2.0
## using the latest 2.0 version
## available on pypi
ANSIBLE_VERSIONS[0]="2.0.2.0"
INSTALL_TYPE[0]="pip"
ANSIBLE_LABEL[0]="v2.0"

## Install Ansible 2.1
## using the latest 2.2 version
## available on pypi
ANSIBLE_VERSIONS[1]="2.1.5.0"
INSTALL_TYPE[1]="pip"
ANSIBLE_LABEL[1]="v2.1"

## Install Ansible 2.2
ANSIBLE_VERSIONS[2]="2.2.1.0"
INSTALL_TYPE[2]="pip"
ANSIBLE_LABEL[2]="v2.2"

# Whats the default version
ANSIBLE_DEFAULT_VERSION="v2.2"

## Create a temp dir
filename=$( echo ${0} | sed 's|/||g' )
my_temp_dir="$(mktemp -dt ${filename}.XXXX)"

curl -s https://raw.githubusercontent.com/ahelal/avm/${SETUP_VERSION}/setup.sh -o $my_temp_dir/setup.sh

## Run the setup
. $my_temp_dir/setup.sh

## Export AWS credentials

export AWS_ACCESS_KEY_ID="AKIAIEVUSPDNZ5HNR4BA"
export AWS_SECRET_ACCESS_KEY="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"
