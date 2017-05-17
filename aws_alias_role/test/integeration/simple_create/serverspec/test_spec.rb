require_relative '../../helper_spec.rb'

before do
  client = Aws::IAM::Client.new()
  resp = client.list_account_aliases({})
  @alias = resp.account_aliases[0]

describe "alias" do
  it { should_not exist }
end