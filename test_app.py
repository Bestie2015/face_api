# content of test_expectation.py
import pytest
import app


@pytest.mark.parametrize("detection, expected", [
    ({'faceRectangle': {'height': 1, 'width': 3}}, 3),
    ({'faceRectangle': {'height': 2, 'width': 3}}, 6),
    ({'faceRectangle': {'height': 2, 'width': 2}}, 4),
])
def test_bounding_box_size(detection, expected):
    assert app.bounding_box_size(detection) == expected


@pytest.mark.parametrize("results, expected", [
    ({'main008.jpg': [{'faceId': '3396a112-1dc4-42a1-bfdb-d9d0b26f7da6',
                       'faceRectangle': {'top': 118, 'height': 136, 'left': 189, 'width': 136}}], 'main002.jpg': [
        {'faceId': '133a628f-9b9f-4c10-88f2-bcf5838938f0',
         'faceRectangle': {'top': 202, 'height': 257, 'left': 167, 'width': 257}}]}, {
         'main002.jpg': {'faceId': '133a628f-9b9f-4c10-88f2-bcf5838938f0',
                         'faceRectangle': {'top': 202, 'height': 257, 'left': 167, 'width': 257}}}),
    ({'main001.jpg': [{'faceId': '26ccd708-2b9c-4fb6-83b1-95455927a684',
                       'faceRectangle': {'top': 315, 'height': 221, 'left': 114, 'width': 221}},
                      {'faceId': '56a04ef8-2558-4de1-9733-d73e78a48547',
                       'faceRectangle': {'top': 633, 'height': 214, 'left': 1201, 'width': 214}}]}, {
         'main001.jpg': {'faceId': '26ccd708-2b9c-4fb6-83b1-95455927a684',
                         'faceRectangle': {'top': 315, 'height': 221, 'left': 114, 'width': 221}}})])
def test_get_best_image(results, expected):
    assert app.get_best_image(results) == expected


@pytest.mark.parametrize("response, expected", [
    ({'main010.jpg': []}, {}),
    ({'main010.jpg': [], 'main001.jpg': [{'main001.jpg': {
        'faceId': '9c612457-db64-4006-9b84-7c77850396cd',
        'faceRectangle': {'top': 315, 'width': 200, 'height': 201, 'left': 114}}}]},
     {'main001.jpg': [{'main001.jpg': {
         'faceId': '9c612457-db64-4006-9b84-7c77850396cd',
         'faceRectangle': {'top': 315, 'width': 200, 'height': 201, 'left': 114}}}]}),

])
def test_remove_no_detections(response, expected):
    assert app.remove_no_detections(response) == expected


@pytest.mark.parametrize("similarities, expected", [
    ({
         "eda2c738-39e4-4d77-9d60-474ec34a553d": [
             {
                 "faceId": "31c1fb48-8768-4db5-8535-78271a583459",
                 "confidence": 0.3336
             }
         ],
         "2efc37db-aa47-4b8e-973d-91854c6d75ca": [
             {
                 "faceId": "dbf8d3a1-57c1-48e5-b97b-930c0d275e81",
                 "confidence": 0.22914
             }
         ],
         "b3eeaf09-a686-427d-a901-8b69c5c7ae5d": [
             {
                 "faceId": "eda2c738-39e4-4d77-9d60-474ec34a553d",
                 "confidence": 0.28184
             }
         ],
         "dbf8d3a1-57c1-48e5-b97b-930c0d275e81": [
             {
                 "faceId": "2efc37db-aa47-4b8e-973d-91854c6d75ca",
                 "confidence": 0.22914
             }
         ],
         "31c1fb48-8768-4db5-8535-78271a583459": [
             {
                 "faceId": "eda2c738-39e4-4d77-9d60-474ec34a553d",
                 "confidence": 0.3335
             }
         ]
     },
     {
         "eda2c738-39e4-4d77-9d60-474ec34a553d": [
             {
                 "faceId": "31c1fb48-8768-4db5-8535-78271a583459",
                 "confidence": 0.3336
             }
         ]
     }
    )
])
def test_get_best_similarity(similarities, expected):
    assert app.get_best_similarity(similarities) == expected


@pytest.mark.parametrize("detections_response, best_similarity, expected", [
    ({'main008.jpg': [{'faceId': '3396a112-1dc4-42a1-bfdb-d9d0b26f7da6',
                       'faceRectangle': {'top': 118, 'height': 136, 'left': 189, 'width': 136}}], 'main002.jpg': [
        {'faceId': '133a628f-9b9f-4c10-88f2-bcf5838938f0',
         'faceRectangle': {'top': 202, 'height': 257, 'left': 167, 'width': 257}}]}, {
         '133a628f-9b9f-4c10-88f2-bcf5838938f0': [
             {'faceId': '3396a112-1dc4-42a1-bfdb-d9d0b26f7da6', 'confidence': 0.10231}]}, {'main008.jpg': [
        {'faceId': '3396a112-1dc4-42a1-bfdb-d9d0b26f7da6',
         'faceRectangle': {'top': 118, 'height': 136, 'left': 189, 'width': 136}}], 'main002.jpg': [
        {'faceId': '133a628f-9b9f-4c10-88f2-bcf5838938f0',
         'faceRectangle': {'top': 202, 'height': 257, 'left': 167, 'width': 257}}]})])
def test_get_most_common_files(detections_response, best_similarity, expected):
    assert app.get_most_common_files(detections_response, best_similarity) == expected
