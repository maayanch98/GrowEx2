import requests
import pytest

BASE_URL = "https://sandbox.meshulam.co.il/api/light/server/1.0/createPaymentProcess"
CLIENT_CHECKOUT_URL_PREFIX = "https://sandbox.meshulam.co.il/product-checkout"
HTTP_OK_STATUS = 200

PAYLOAD = {
        "pageCode": "e19e0b687744",
        "userId": "52e95954cd5c1311",
        "sum": "1",
        "paymentNum": "1",
        "description": "ORDER123",
        "pageField[fullName]": "שם מלא",
        "pageField[phone]": "0534738605",
        "pageField[email]": "debbie@meshulam.co.il"
    }


def test_legal_payment():
    body_req = PAYLOAD
    response = requests.post(BASE_URL, data=body_req)
    assert response.status_code == HTTP_OK_STATUS, f"https status is {response.status_code} instead of 200"

    try:
        data = (response.json())['data']
        result_url = data['url']
        assert result_url.startswith(CLIENT_CHECKOUT_URL_PREFIX), f"got illegal url for product checkout: {result_url}"
    except KeyError as ke:
        assert False, f"response does contain a legal values: {ke}"


@pytest.mark.parametrize("sum", [
    0, -7, "w", "!"
])
def test_non_legal_sum_for_payment(sum):
    body_req = PAYLOAD.copy()
    body_req["sum"] = str(sum)
    response = requests.post(BASE_URL, data=body_req)
    assert response.status_code == HTTP_OK_STATUS, f"https status is {response.status_code} instead of 200"

    try:
        data = (response.json())['err']
        assert data != '', "got success message from server instead of error"
        err_msg = data['message']
        assert err_msg == "לא ניתן לשלם בסכום הנמוך מ- 0", f"didn't receive error message about the sum: {err_msg}"
    except KeyError as ke:
        assert False, f"response does contain a legal values: {ke}"


@pytest.mark.parametrize("payment_num", [
    0, -1.5, -7, 1.5, "!"
])
def test_non_legal_payment_num_for_payment(payment_num):
    body_req = PAYLOAD.copy()
    body_req["paymentNum"] = str(payment_num)
    response = requests.post(BASE_URL, data=body_req)
    assert response.status_code == HTTP_OK_STATUS, f"https status is {response.status_code} instead of 200"

    try:
        data = (response.json())['err']
        assert data != '', "got success message from server instead of error"
        err_msg = data['message']
        assert err_msg == "סוג תשלום לא תואם מספר תשלומים", f"didn't receive error message about the payment num: {err_msg}"
    except KeyError as ke:
        assert False, f"response does contain a legal values: {ke}"


@pytest.mark.parametrize("field_name", [
    "pageCode", "userId", "sum", "paymentNum"
])
def test_field_missing_for_payment(field_name):
    body_req = PAYLOAD.copy()
    del body_req[field_name]
    response = requests.post(BASE_URL, data=body_req)
    assert response.status_code == HTTP_OK_STATUS, f"https status is {response.status_code} instead of 200"

    try:
        data = (response.json())['err']
        assert data != '', "got success message from server instead of error"
        err_msg = data['message']
        assert err_msg.startswith("חסרים נתונים"), f"didn't receive error message of missing data. instead: {err_msg}"
    except KeyError as ke:
        assert False, f"response does contain a legal values: {ke}"
