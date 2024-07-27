from request import RequestPayload, RequestType, get_sample_request_payload


def test_text_request_encode() -> None:
    req = get_sample_request_payload(RequestType.TEXT)

    encoded_req = req.encode()

    decoded_req = RequestPayload.decode(encoded_req)

    assert req.message_id == decoded_req.message_id
    assert req.text == decoded_req.text

    assert req.audio == None
    assert decoded_req.audio == None

    assert req.video == None
    assert decoded_req.video == None


def test_audio_request_encode() -> None:
    req = get_sample_request_payload(RequestType.AUDIO)

    encoded_req = req.encode()

    decoded_req = RequestPayload.decode(encoded_req)

    assert req.message_id == decoded_req.message_id
    assert req.audio == decoded_req.audio

    assert req.text == None
    assert decoded_req.text == None

    assert req.video == None
    assert decoded_req.video == None


def test_video_request_encode() -> None:
    req = get_sample_request_payload(RequestType.VIDEO)

    encoded_req = req.encode()

    decoded_req = RequestPayload.decode(encoded_req)

    assert req.message_id == decoded_req.message_id
    assert req.video == decoded_req.video

    assert req.text == None
    assert decoded_req.text == None

    assert req.audio == None
    assert decoded_req.audio == None
