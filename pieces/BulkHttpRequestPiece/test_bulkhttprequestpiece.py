from domino.testing import piece_dry_run
import base64
import json


def test_bulkhttprequest_get_multiple():
    input_data = {
        'urls': [
            'https://jsonplaceholder.typicode.com/posts/1',
            'https://jsonplaceholder.typicode.com/posts/2',
        ],
        'method': 'GET',
    }
    piece_output = piece_dry_run(
        piece_name="BulkHttpRequestPiece",
        input_data=input_data
    )
    results = piece_output['base64_bytes_data_list']
    errors = piece_output['errors']
    assert len(results) == 2
    assert all(e == "" for e in errors)
    for b64_str in results:
        decoded = json.loads(base64.b64decode(b64_str))
        assert 'id' in decoded


def test_bulkhttprequest_empty_list():
    input_data = {
        'urls': [],
        'method': 'GET',
    }
    piece_output = piece_dry_run(
        piece_name="BulkHttpRequestPiece",
        input_data=input_data
    )
    assert piece_output['base64_bytes_data_list'] == []
    assert piece_output['errors'] == []


def test_bulkhttprequest_with_error():
    input_data = {
        'urls': [
            'https://jsonplaceholder.typicode.com/posts/1',
            'https://httpbin.org/status/404',
        ],
        'method': 'GET',
    }
    piece_output = piece_dry_run(
        piece_name="BulkHttpRequestPiece",
        input_data=input_data
    )
    results = piece_output['base64_bytes_data_list']
    errors = piece_output['errors']
    assert len(results) == 2
    # First URL succeeds
    assert results[0] != ""
    assert errors[0] == ""
    # Second URL fails (404)
    assert results[1] == ""
    assert errors[1] != ""
