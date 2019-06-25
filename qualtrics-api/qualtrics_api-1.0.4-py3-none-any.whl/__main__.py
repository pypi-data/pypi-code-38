# qualtrics/__main__.py
import logging

from qualtrics.qualtrics_api import *

# This section adds logging capabilities to this script.
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - PID[%(process)d] - [%(levelname)s]: %(message)s')
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)


def main(argv=None):
    parser = get_parser()
    args = parser.parse_args(argv)
    data_center = args.datacenter
    token = args.token
    survey_id = args.survey
    organization = args.organization
    # TODO: Need to find a workaround on how to identify this list of questions to filter out.
    questions = []
    response_create = create_export_response(data_center_id=data_center, token=token, survey_id=survey_id)
    logger.info('The result of the request for the survey is: %s', response_create)
    progress_id = response_create['result']['progressId']
    file_Id = get_export_responses_progress(data_center_id=data_center, token=token, survey_id=survey_id,
                                            progress_id=progress_id)
    logger.info('The file ID associated to all the responses of the survey is: %s', file_Id)
    json_responses_survey = get_export_file(data_center_id=data_center, token=token, survey_id=survey_id,
                                            file_id=file_Id)
    logger.info('Number of responses found in the survey: %s', len(json_responses_survey['responses']))
    logger.info('All the responses from the survey in json format: %s', json_responses_survey['responses'])


if __name__ == "__main__":
    main()
