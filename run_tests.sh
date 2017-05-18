#!/bin/bash
# set -e


function usage()
{
    echo ""
    echo "Usage:"
    echo ""
    echo "./run_tests.sh"
    echo "    -h --help"
    echo "    --access-key=AWS_ACCESS_KEY_ID"
    echo "    --access-secret=AWS_SECRET_ACCESS_KEY"
    echo ""
}

if [[ $# -ne 2 ]]
	then
	usage
	exit
fi

while [[ "$1" != "" ]]
do
    PARAM=`echo $1 | awk -F= '{print $1}'`
    VALUE=`echo $1 | awk -F= '{print $2}'`

	case $PARAM in
		-h | --help)
		    usage
		    exit
		    ;;
	    --access-key)
		    AWS_ACCESS_KEY_ID=$VALUE
		    ;;
	    --access-secret)
		    AWS_SECRET_ACCESS_KEY=$VALUE
		    ;;
	    *)
	        echo "ERROR: unknown parameter \"$PARAM\""
	        usage
	        exit 1
	        ;;
	esac
	shift
done


echo "Setting up ansible virtual environments"

VIRTUAL_ENV="aws_alias_test"
SETUP_VERSION="v0.0.5"
ROLE_DIR="$(pwd)/aws_alias_role"

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

# Run the setup
. $my_temp_dir/setup.sh

echo "Setting AWS credentials"
export AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID
export AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY

echo "installing dependencies v2.0"
$(avm path v2.0)/pip install -r ${ROLE_DIR}/requirements.txt

echo "installing dependencies v2.1"
$(avm path v2.1)/pip install -r ${ROLE_DIR}/requirements.txt

echo "installing dependencies v2.2"
$(avm path v2.2)/pip install -r ${ROLE_DIR}/requirements.txt

echo "Running unit tests v2.0"
$(avm path v2.0)/nosetests -w ${ROLE_DIR}/library

echo "Running unit tests v2.1"
$(avm path v2.1)/nosetests -w ${ROLE_DIR}/library

echo "Running unit tests v2.2"
$(avm path v2.2)/nosetests -w ${ROLE_DIR}/library

cd aws_alias_role
echo "Installing integeration test dependencies"
bundle install
echo "Running integeration tests"
# kitchen test