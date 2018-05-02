import os
from flask import Flask, request, jsonify, Response
import requests
import logging
import json
from pathlib import Path
from requests_futures.sessions import FuturesSession
from PIL import Image

session = FuturesSession()

app = Flask(__name__)

face_api_url = 'https://westcentralus.api.cognitive.microsoft.com/face/v1.0/detect'
find_similar_url = 'https://westcentralus.api.cognitive.microsoft.com/face/v1.0/findsimilars'
headers = {
    'Ocp-Apim-Subscription-Key': os.environ['AZURE_FACE_API_KEY']
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


def get_best_image(most_common_files):
    ratio_detection = 0
    best_detection = {}
    best_image_filename = None
    for file_name, detections in most_common_files.items():
        if len(detections) == 2:
            if bounding_box_size(detections[0]) > bounding_box_size(detections[1]):
                return {file_name: detections[0]}
            else:
                return {file_name: detections[1]}
        else:
            image = Image.open('./faces/' + file_name)
            image_width, image_height = image.size
            ratio = bounding_box_size(detections[0]) / (image_width * image_height)
            if ratio > ratio_detection:
                ratio_detection = ratio
                best_detection = detections[0]
                best_image_filename = file_name
    return {best_image_filename: best_detection}


def get_face_detection(binary_file_list):
    results = {}
    responses = {}
    headers['Content-Type'] = 'application/octet-stream'
    for file_name, data in binary_file_list.items():
        responses[file_name] = session.post(face_api_url, params={}, headers=headers, data=data)
    for file_name, response in responses.items():
        try:
            r = response.result()
            r.raise_for_status()
            results[file_name] = json.loads(r.text)
        except requests.exceptions.RequestException as e:
            logging.error("Error while getting Face API detection for {0}: {1}".format(file_name, e.strerror))
    return results


def read_files(files):
    binary_file_list = {}
    for file in files:
        try:
            data = open('./faces/' + file, 'rb').read()
            binary_file_list[file] = data
        except OSError as e:
            logging.error("Error while reading file {0}: {1}".format(file, e.strerror))
    return binary_file_list


def get_face_ids(detections_response):
    face_ids = {}
    for file_name, detections in detections_response.items():
        face_ids[file_name] = [x['faceId'] for x in detections]
    return face_ids


def get_face_ids_array(face_ids):
    face_ids_array = []
    for file_name, ids in face_ids.items():
        face_ids_array.extend(ids)
    return face_ids_array


def get_similarities(face_ids_array):
    results = {}
    for i in range(0, len(face_ids_array)):
        face_id = face_ids_array[i]
        face_ids = [x for j, x in enumerate(face_ids_array) if i != j]
        try:
            headers['Content-Type'] = 'application/json'
            r = requests.post(find_similar_url, params={}, headers=headers, json={
                "faceId": face_id,
                "faceIds": face_ids,
                "mode": "matchFace",
                "maxNumOfCandidatesReturned": 1
            })
            r.raise_for_status()
            results[face_id] = json.loads(r.text)
        except requests.exceptions.RequestException as e:
            logging.error("Error while getting Face API detection for {0}".format(e.strerror))
    return results


def get_best_similarity(similarities):
    face_id_match = None
    confidence = 0
    for face_id, similarity in similarities.items():
        if similarity[0]['confidence'] > confidence:
            confidence = similarity[0]['confidence']
            face_id_match = face_id
    if face_id_match is None:
        return {}
    else:
        return {face_id_match: similarities[face_id_match]}


def get_most_common_files(detections_response, best_similarity):
    most_common_files = {}
    face_id_one, face_id_two = list(best_similarity.keys())[0], list(best_similarity.items())[0][1][0]['faceId']
    for file_name, detections in detections_response.items():
        for detection in detections:
            if detection['faceId'] == face_id_one or detection['faceId'] == face_id_two:
                if file_name not in most_common_files:
                    most_common_files[file_name] = [detection]
                else:
                    most_common_files[file_name].append(detection)
    return most_common_files


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
        logging.error("ERROR: all call to face detection api failed")
        return 'Internal Server Error', 500

    detections_response = remove_no_detections(response)
    if detections_response == {}:
        return "Face API found 0 detections", 200

    face_ids = get_face_ids(detections_response)

    face_ids_array = get_face_ids_array(face_ids)
    if len(face_ids_array) == 1:
        return 'There is only one face in photos, file: {0}'.format(list(face_ids.keys())[0]), 200

    similarities = get_similarities(face_ids_array)
    if similarities == {}:
        logging.error("ERROR: all call to face similarity api failed")
        return 'Internal Server Error', 500

    best_similarity = get_best_similarity(similarities)
    if best_similarity == {}:
        return 'Face API found 0 similarities', 200

    most_common_files = get_most_common_files(detections_response, best_similarity)

    meta_data = get_best_image(most_common_files)

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
