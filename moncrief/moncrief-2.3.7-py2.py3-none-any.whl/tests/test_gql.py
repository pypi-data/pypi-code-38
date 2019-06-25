import pytest

from algernon.aws.gql import GqlSigner, GqlNotary


@pytest.mark.gql
@pytest.mark.usefixtures('lambda_environment')
class TestGql:
    def test_gql_signer(self):
        signer = GqlSigner('mh5syterirdvzji7tdbrrmpe7m.appsync-api.us-east-1.amazonaws.com')
        header = signer.generate_headers('some_query', {'some_variable': 'some_value'})
        assert header

    def test_notary(self):
        endpoint = 'mh5syterirdvzji7tdbrrmpe7m.appsync-api.us-east-1.amazonaws.com'
        notary = GqlNotary(endpoint)
        query = """
            query getEvent($flow_id: String!, $token: String){
                listStateEntries(flow_id: $flow_id, nextToken: $token){
                    items{
                        state_id
                    }
                }
            }
        """
        variables = {'flow_id': 'some_flow_id'}
        results = notary.send(query, variables)
        assert results
