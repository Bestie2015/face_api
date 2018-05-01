import os
from flask import Flask, request, jsonify, Response
import requests
import logging
import json
from pathlib import Path
from requests_futures.sessions import FuturesSession

session = FuturesSession()

app = Flask(__name__)

face_api_url = 'https://westcentralus.api.cognitive.microsoft.com/face/v1.0/detect'
headers = {
    'Ocp-Apim-Subscription-Key': os.environ['AZURE_FACE_API_KEY'],
    'Content-Type': 'application/octet-stream'
}


def get_uniq_files(file_list):
    files = []
    for file_name in file_list:
        my_file = Path("./faces/{}".format(file_name))
        if my_file.is_file():
            files.append(file_name)
        else:
            logging.info("{0} is not a file - the path doesn’t exist or is a broken symlink".format(file_name))
    return list(set(files))


def bounding_box_size(detection):
    return detection['faceRectangle']['height'] * detection['faceRectangle']['width']


def remove_no_detections(response):
    valid_detections = {}
    for file_name, result in response.items():
        if len(result):
            valid_detections[file_name] = result
        else:
            logging.info("{0} has 0 face detections".format(file_name))
    return valid_detections


def get_best_image(results):
    meta_data = {}
    max_size = 0
    largest_detection = None
    largest_detection_filename = None
    for file_name, result in results.items():
        for detection in result:
            temp_box_size = bounding_box_size(detection)
            if temp_box_size > max_size:
                largest_detection_filename = file_name
                largest_detection = detection
                max_size = temp_box_size
    meta_data[largest_detection_filename] = largest_detection
    return meta_data


def get_face_detection(binary_file_list):
    results = {}
    responses = {}
    for file_name, data in binary_file_list.items():
        responses[file_name] = session.post(face_api_url, params={}, headers=headers, data=data)
    for file_name, response in responses.items():
        try:
            r = response.result()
            r.raise_for_status()
            results[file_name] = json.loads(r.text)
        except requests.exceptions.RequestException as e:
            logging.error("Error while getting Face API detection for {0}: {1}".format(file_name, e))
    return results


def read_files(files):
    binary_file_list = {}
    for file in files:
        try:
            data = open('./faces/' + file, 'rb').read()
            binary_file_list[file] = data
        except OSError as e:
            logging.error("Error while reading file {0}: {1}".format(file, e))
    return binary_file_list


@app.route("/healthcheck")
def healthcheck():
    return "Ok", 200


@app.route('/', methods=['POST'])
def get():
    file_list = request.get_json()
    if file_list is None or not isinstance(file_list, list):
        logging.info("Bad Request: Not json")
        return "Bad Request", 400

    files = get_uniq_files(file_list)
    if len(files) == 0:
        logging.info("Bad Request: All files are not exist")
        return "All files are not exist", 404

    binary_file_list = read_files(files)
    if len(binary_file_list) == 0:
        logging.info("Bad Request: Error while reading files")
        return "Error while reading files", 404

    response = get_face_detection(binary_file_list)
    if response == {}:
        return 'Internal Server Error', 500

    detections_response = remove_no_detections(response)
    if detections_response == {}:
        return "Face API found 0 detections", 200

    meta_data = get_best_image(detections_response)

    return jsonify(meta_data)


@app.errorhandler(404)
def page_not_found(error):
    return 'Not Found', 404


@app.errorhandler(500)
def internal_exception_handler(error):
    return 'Internal Server Error', 500


if __name__ == "__main__":
    logging.basicConfig(filename='logfile.log', level=logging.DEBUG)
    logging.info('API is Running')
    app.run(host='0.0.0.0', port=5002)
