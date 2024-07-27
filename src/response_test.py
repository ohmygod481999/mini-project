from response import ResponsePayload, ResponseType, get_sample_response_payload


def test_response_encode_text_audio_image() -> None:
    resp = get_sample_response_payload(ResponseType.TEXT_AUDIO_IMAGE)

    encoded_resp = resp.encode()

    decoded_resp = ResponsePayload.decode(encoded_resp)

    assert resp.message_id == decoded_resp.message_id
    assert resp.text == decoded_resp.text
    assert resp.image == decoded_resp.image
    assert resp.audio == decoded_resp.audio


def test_response_encode_text_audio() -> None:
    resp = get_sample_response_payload(ResponseType.TEXT_AUDIO)

    encoded_resp = resp.encode()

    decoded_resp = ResponsePayload.decode(encoded_resp)

    assert resp.message_id == decoded_resp.message_id
    assert resp.text == decoded_resp.text
    assert resp.image == decoded_resp.image
    assert resp.audio == decoded_resp.audio
    assert resp.image == None
    assert decoded_resp.image == None


def test_response_encode_text() -> None:
    resp = get_sample_response_payload(ResponseType.TEXT)

    encoded_resp = resp.encode()

    decoded_resp = ResponsePayload.decode(encoded_resp)

    assert resp.message_id == decoded_resp.message_id
    assert resp.text == decoded_resp.text
    assert resp.image == decoded_resp.image
    assert resp.audio == decoded_resp.audio

    assert resp.image == None
    assert decoded_resp.image == None

    assert resp.audio == None
    assert decoded_resp.audio == None
