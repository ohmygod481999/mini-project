from response import ResponsePayload, ResponseType, get_sample_response_payload


def test_encode() -> None:
    resp = get_sample_response_payload(ResponseType.TEXT_AUDIO_IMAGE)

    encoded_resp = resp.encode()

    decoded_resp = ResponsePayload.decode(encoded_resp)

    assert resp.message_id == decoded_resp.message_id
    assert resp.text == decoded_resp.text
    assert resp.image == decoded_resp.image
    assert resp.audio == decoded_resp.audio
