import requests


def send_request(url: str, method: str) -> dict:
    if method == 'GET':
        response = requests.get(url)
    elif method == 'POST':
        response = requests.post(url)
    else:
        raise ValueError

    return response.json()

