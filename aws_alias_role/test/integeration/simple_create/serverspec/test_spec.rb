require_relative '../../helper_spec.rb'

before do
  client = Aws::IAM::Client.new()
  resp = client.list_account_aliases({})
  @aws_account_alias = resp.account_aliases[0]
end

describe aws_account_alias do
  it "AWS account alias should be set" do
    expect(@aws_account_alias).to eql("test-alias-12345")
  end
end