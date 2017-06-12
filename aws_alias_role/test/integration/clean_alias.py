#!/usr/bin/python

import boto3
import os

def clean_aliases():
	aws_access_key_id = os.environ["AWS_ACCESS_KEY_ID"]
	aws_secret_access_key = os.environ["AWS_SECRET_ACCESS_KEY"]
	client =  boto3.client("iam",
	    aws_access_key_id=aws_access_key_id,
	    aws_secret_access_key=aws_secret_access_key)

	resp = client.list_account_aliases()
	print resp
	if resp["AccountAliases"]:
		client.delete_account_alias(AccountAlias=resp["AccountAliases"][0])

if __name__ == "__main__":
	clean_aliases()