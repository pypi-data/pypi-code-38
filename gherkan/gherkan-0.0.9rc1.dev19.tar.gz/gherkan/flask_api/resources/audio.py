from flask import jsonify, request, Response
from flask_restful import Resource, reqparse, abort
import os
from .. import API_FSA
import logging


class Audio(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument("language", type=str, choices=("en", "cs"), required=True)

    def post(self):
        """
        request = {
            "language": "en",
            "description": "desc text",
            "background", "optional background text"
            }
        E.g.: curl -F file=@nl_audio_file.wav -F 'data={"language": "en", "description": "desc text", "background", ""}'  <URI>/audio

        response = {
            "language": "en",
            "description": "desc text",
            "background", "optional background text",
            "transcript": "text extracted from audio"
        }
        """
        args = self.parser.parse_args()

        for _, value in request.files.items():
            audioFileName = os.path.join(API_FSA.audioFolder, value.filename)
            value.save(audioFileName)
        try:
            transcript = API_FSA.receiveAudio(audioFileName, args["language"])
        except Exception as error:
            errorMessage = "An error occurred while processing the audio! Error: '{}'".format(str(error))
            logging.exception(errorMessage)
            abort(400, message=errorMessage)
        else:
            return {
                "language": args["language"],
                "transcript": transcript
                }
