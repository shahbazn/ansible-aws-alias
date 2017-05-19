import ansible
import datetime
import json
import mock
import os
import unittest

from ansible.module_utils import basic
from botocore.stub import Stubber
from boto3 import client as aws_client
from iam_alias import (get_user_id,
	get_account_alias,
	set_account_alias,
	delete_account_alias)
from packaging import version

VERSION_2_0 = version.parse(ansible.__version__) < version.parse("2.1.0")

class TestIamAlias(unittest.TestCase):
	def setUp(self):
		self.aws_account_alias = ""
		self.aws_account_state = "present"
		self.aws_access_key = "test-key"
		self.aws_secret_key = "test-secret"

		# Set `test-alias` as an alias value
		# which is already being used by some
		# other user
		self.existing_alias = "test-alias"

		self.module = self._get_module()
		self.client = aws_client("iam",
			aws_access_key_id=self.aws_access_key,
			aws_secret_access_key=self.aws_secret_key)
		self.stubber = Stubber(self.client)

	def _resp_meta(self, http_code):
		# Response meta data default
		resp_meta = {
			"HTTPStatusCode": http_code, 
			"RequestId": "test-request", 
		}

		return resp_meta

	def _set_create_response(self, alias):
		method = "create_account_alias"
		expected_params = {"AccountAlias":alias}

		if alias == self.aws_account_alias or alias == self.existing_alias:

			msg = "The account alias `%s` already exists." % alias
			error = "EntityAlreadyExists"
			http_code = 409
			resp_meta = self._resp_meta(http_code)
			resp = {"ResponseMetadata": resp_meta}
			error = {
				"Message": msg, 
				"Code": error, 
				"Type": "Sender"
			}

			self.stubber.add_client_error(method, error, msg, http_code, error, expected_params)
			self.stubber.activate()

		if alias != self.aws_account_alias:
			http_code = 200
			resp_meta = self._resp_meta(http_code)
			resp = {"ResponseMetadata": resp_meta}

			self.stubber.add_response('create_account_alias', resp, expected_params)
			self.stubber.activate()

	def _set_delete_response(self, alias):
		method = "delete_account_alias"
		expected_params = {"AccountAlias":alias}
		http_code = 200
		resp_meta = self._resp_meta(http_code)
		
		if alias == self.aws_account_alias:
			resp = {"ResponseMetadata": resp_meta}

			self.stubber.add_response(method, resp, expected_params)
			self.stubber.activate()

		if alias != self.aws_account_alias:
			msg = "The account alias %(alias)s cannot be found."
			error = "NoSuchEntity"
			http_code = 404
			resp_meta = self._resp_meta(http_code)
			resp = {"ResponseMetadata": resp_meta}
			error = {
				"Message": msg, 
				"Code": error, 
				"Type": "Sender"
			}

			self.stubber.add_client_error(method, error, msg, http_code)
			self.stubber.activate()

	def _set_get_alias_response(self):
		method = "list_account_aliases"
		aliases = []
		http_code = 200
		if self.aws_account_alias:
			aliases.append(self.aws_account_alias)

		resp_meta = self._resp_meta(http_code)
		resp = {
			"AccountAliases": aliases, 
	        "IsTruncated": False,
			"ResponseMetadata": resp_meta
		}

		self.stubber.add_response(method, resp, {})
		self.stubber.activate()

	def _set_get_user_respone(self):
		method = "get_user"
		http_code = 200
		resp_meta = self._resp_meta(http_code)
		resp = {
			"User": {
	            "UserName": "test_user_name",
	            "UserId": "test_user_id_1234",
	            "Path": "/", 
	            "CreateDate": datetime.datetime(2016, 1, 20, 22, 9),
	            "Arn": "arn:aws:iam::123456789012:user/test_user_Nme"
	        },
			"ResponseMetadata": resp_meta
		}

		self.stubber.add_response(method, resp, {})
		self.stubber.activate()

	def _get_module(self):
		# Set Ansible Module Arguments and
		# ensure compatibility with Ansible 2.0.2.0
		if VERSION_2_0:
			basic.MODULE_COMPLEX_ARGS = json.dumps(dict(
				aws_account_alias=self.aws_account_alias,
				aws_account_state=self.aws_account_state,
				aws_access_key=self.aws_access_key,
				aws_secret_key=self.aws_secret_key
				)
			)
		else:
			basic._ANSIBLE_ARGS = json.dumps(dict(
				ANSIBLE_MODULE_ARGS=dict(
					aws_account_alias=self.aws_account_alias,
					aws_account_state=self.aws_account_state,
					aws_access_key=self.aws_access_key,
					aws_secret_key=self.aws_secret_key
					)
				))

		argument_spec = dict(
			aws_account_alias=dict(default=None, required=False),
			aws_account_state=dict(
				default=None, required=True, choices=["present", "absent"]),
			aws_access_key=dict(default=None, required=True),
			aws_secret_key=dict(default=None, required=True),
			)

		module = basic.AnsibleModule(
			argument_spec=argument_spec
			)
		return module

	def test_create_alias(self):
		alias = "test-alias-12345"
		client = self.client
		module = self.module

		self._set_create_response(alias)
		self.assertTrue(set_account_alias(module, client, alias))

	def test_create_existing_alias(self):
		alias = self.existing_alias
		client = self.client
		module = self.module

		self._set_create_response(alias)
		with self.assertRaises(SystemExit):
			set_account_alias(module, client, alias)

	def test_create_invalid_alias(self):
		alias = "test_alias"
		client = self.client
		module = self.module

		with self.assertRaises(SystemExit):
			set_account_alias(module, client, alias)

	def test_update_alias(self):
		alias = "test-alias-12345"
		new_alias = alias + "-new"
		client = self.client
		module = self.module

		self._set_create_response(alias)
		self.assertTrue(set_account_alias(module, client, alias))
		self.aws_account_alias = alias

		self._set_create_response(new_alias)
		self.assertTrue(set_account_alias(module, client, new_alias))

	def test_delete_alias(self):
		alias = "test-alias-12345"
		client = self.client
		module = self.module

		self._set_create_response(alias)
		self.assertTrue(set_account_alias(module, client, alias))
		self.aws_account_alias = alias

		self._set_delete_response(alias)
		self.assertTrue(delete_account_alias(module, client, alias))

	def test_delete_wrong_alias(self):
		alias = "test-alias-12345"
		wrong_alias = alias + "-wrong"
		state = "absent"
		client = self.client
		module = self.module


		self._set_create_response(alias)
		self.assertTrue(set_account_alias(module, client, alias))
		self.aws_account_alias = alias

		self._set_delete_response(wrong_alias)
		with self.assertRaises(SystemExit):
			delete_account_alias(module, client, wrong_alias)

	def test_delete_alias_when_not_created(self):
		alias = "test-alias-12345"
		client = self.client
		module = self.module

		self._set_delete_response(alias)
		with self.assertRaises(SystemExit):
			delete_account_alias(module, client, alias)

	def test_get_alias_when_not_created(self):
		client = self.client
		module = self.module

		self._set_get_alias_response()
		self.assertEqual("", get_account_alias(module, client))

	def test_get_alias(self):
		alias = "test-alias-12345"
		client = self.client
		module = self.module

		self._set_create_response(alias)
		self.assertTrue(set_account_alias(module, client, alias))
		self.aws_account_alias = alias

		self._set_get_alias_response()
		self.assertEqual(alias, get_account_alias(module, client))

	def test_get_user_id(self):
		client = self.client
		module = self.module

		self._set_get_user_respone()
		# User ID is expected to be of length 16
		self.assertEqual("test_user_id_1234", get_user_id(module, client))

