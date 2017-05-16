import boto3
import placebo
import json
import mock
import os
import unittest

from ansible.module_utils import basic
from iam_alias import (get_user_id,
	get_account_alias,
	set_account_alias,
	delete_account_alias)

class TestIamAlias(unittest.TestCase):
	def setUp(self):
		self.aws_account_alias = ""
		self.aws_account_state = "present"
		# If `PLACEBO_RECORD` is set to `record`
		# must use `aws_access_key` and `aws_secret_key`
		# from ENVIRONMENT variables `AWS_ACCESS_KEY_ID`
		# and `AWS_SECRET_ACCESS_KEY`
		if os.getenv("PLACEBO_RECORD")=="record":
			self.aws_access_key = os.getenv("AWS_ACCESS_KEY_ID")
			self.aws_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")

			if not self.aws_access_key or not self.aws_secret_key:
				raise Exception("Running unit test in `record` mode"
					" requires credentials are set as environment variables"
					" `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY`")
		else:
			self.aws_access_key = "test-key"
			self.aws_secret_key = "test-secret"

		self.client = self._boto3_client()
		self.module = self._get_module()

		# Each Test starts with a clean account
		# alias state so before each test any
		# set account alias should be cleared
		self._clear_alias()

	def tearDown(self):
		# Reset Ansible Module arguments after
		# each test run
		self.aws_account_alias = ""
		self.aws_account_state = "present"
		self.aws_access_key = "test-key"
		self.aws_secret_key = "test-secret"

		self.pill.stop()

	def _clear_alias(self):
		client = self.client
		module = self.module

		alias = get_account_alias(module, client)

		if alias:
			delete_account_alias(module, client, alias)

	def _boto3_client(self):
		"""This fixture puts a recording/replaying harness around `boto3.Session.client`

		Placebo_client returns a boto3 session that in recording or replaying mode,
		depending on the PLACEBO_RECORD environment variable. Unset PLACEBO_RECORD
		(the common case or just running tests) will put placebo in replay mode, set
		PLACEBO_RECORD to any value to turn off replay & operate on real AWS resources.

		The recorded sessions are stored in the test file's directory, under the
		namespace `fixtures/{test function name}` to
		distinguish them.
		"""
		session = boto3.session.Session()

		recordings_path = os.path.join(
			os.path.dirname(os.path.realpath(__file__)),
			"fixtures"
			)

		try:
			# make sure the directory for placebo test recordings is available
			os.makedirs(recordings_path)
		except OSError as e:
			if e.errno != os.errno.EEXIST:
				raise

		self.pill = placebo.attach(session, data_path=recordings_path)
		if os.getenv("PLACEBO_RECORD")=="record":
			self.pill.record()
		else:
			self.pill.playback()

		client = session.client("iam",
			aws_access_key_id=self.aws_access_key,
			aws_secret_access_key=self.aws_secret_key)

		return client


	def _get_module(self):
		# Set Ansible Module Arguments
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

	def test_create_valid_alias(self):
		self.aws_account_alias = "test-alias-12345"
		self.aws_account_state = "present"

		alias = self.aws_account_alias
		client = self.client
		module = self.module
		set_account_alias(module, client, alias)
