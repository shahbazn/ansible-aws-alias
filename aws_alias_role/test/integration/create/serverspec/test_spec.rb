require_relative '../../helper_spec.rb'
require 'aws-sdk'

describe "AWS account alias should be set" do
	# region is hard coded here because while setting
	# alias region is irrelevant
	client = Aws::IAM::Client.new(region: 'eu-west-1')
  	resp = client.list_account_aliases({})
  	aws_account_alias = resp.account_aliases[0]
    it { expect(aws_account_alias).to eql("test-alias-12345") }
end