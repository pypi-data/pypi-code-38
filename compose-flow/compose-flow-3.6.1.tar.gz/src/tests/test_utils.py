from unittest import TestCase

from compose_flow import utils


class RenderTestCase(TestCase):
    def test_multiple_subs_on_same_line(self, *mocks):
        env = {'JOB_NAME': 'the-job', 'BUILD_NUMBER': '1234'}

        content = (
            '      - /tmp/jenkins/${JOB_NAME}/${BUILD_NUMBER}:/usr/local/src/results'
        )

        rendered = utils.render(content, env=env)

        expected = f'      - /tmp/jenkins/{env["JOB_NAME"]}/{env["BUILD_NUMBER"]}:/usr/local/src/results'

        self.assertEqual(expected, rendered)
