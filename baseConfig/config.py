import requests


def findData(url, body):
    reqBody = {
        "query": body
    }
    res = requests.post(url=url, json=reqBody)
    return res.text
