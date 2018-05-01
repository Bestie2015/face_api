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
    (
            {'main001.jpg': [
                {'faceId': '9c612457-db64-4006-9b84-7c77850396cd',
                 'faceRectangle': {'top': 315, 'width': 200, 'height': 201, 'left': 114}},
                {'faceId': 'ffd6cc59-9f7c-45e7-a68e-65c440ced48e',
                 'faceRectangle': {'top': 633, 'width': 201, 'height': 200, 'left': 1201}}
            ],
                'main002.jpg': [
                    {'faceId': 'c181e1ba-47d4-47d9-a447-c6e83a99fd90',
                     'faceRectangle': {'top': 202, 'width': 200, 'height': 202, 'left': 167}}]},
            {'main002.jpg': {
                'faceId': 'c181e1ba-47d4-47d9-a447-c6e83a99fd90',
                'faceRectangle': {'top': 202, 'width': 200, 'height': 202, 'left': 167}}}),
    (
            {'main001.jpg': [
                {'faceId': '9c612457-db64-4006-9b84-7c77850396cd',
                 'faceRectangle': {'top': 315, 'width': 200, 'height': 201, 'left': 114}},
                {'faceId': 'ffd6cc59-9f7c-45e7-a68e-65c440ced48e',
                 'faceRectangle': {'top': 633, 'width': 201, 'height': 200, 'left': 1201}}
            ],
                'main002.jpg': [
                    {'faceId': 'c181e1ba-47d4-47d9-a447-c6e83a99fd90',
                     'faceRectangle': {'top': 202, 'width': 200, 'height': 200, 'left': 167}}]},
            {'main001.jpg': {
                'faceId': '9c612457-db64-4006-9b84-7c77850396cd',
                'faceRectangle': {'top': 315, 'width': 200, 'height': 201, 'left': 114}}}),
])
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
