import json

from baseConfig.GraphQL import Graph
from baseConfig.config import findData
from baseConfig.urls import Urls
from baseConfig.timeStamp import getChangeLate


def getPoolData():
    url = input("url:")
    if not url:
        url = Urls.testGraphQLUrl
    res = findData(url=url, body=Graph.poolsQuery)
    res = json.loads(res)
    return res


def caculatePoolData():
    dicts = getPoolData()
    for index in dicts["data"]["pools"]:
        poolList = {}
        name = index["name"]
        tvl = float(index["tvlUSD"])
        _0hTvlList = index["_0hTvl"]
        _24VolList = index["_0hTvl"]
        _24_48VolList = index["_0hTvl"]
        _7dVolList = index["_0hTvl"]

        poolList["poolName"] = {
            "name": name,
            "TVL": tvl,
            "TVLChange": 0,
            "Volume24H": 0,
            "VolumeChange": 0,
            "Volume7D": 0,
            "Fee24H": 0,
            "Fee24HChange": 0,
            "FeeAPR": 0,
            "FeeAPRChange": 0
        }

        for analytics in _0hTvlList:
            _0hTvl = float(analytics["tvlUSD"])

            pool = poolList["poolName"]
            pool["TVLChange"] = getChangeLate(tvl, _0hTvl)

        _24Vol, _24Fee, _24FeeApr, _24Tvl = 0, 0, 0, 0
        for analytics in _24VolList:
            _24Vol = float(analytics["txVolumeUSD"])
            _24Fee = float(analytics["feesUSD"])
            _24Vol += _24Vol
            _24Fee += _24Fee

        if (tvl != 0) & (_24VolList != []):
            _24FeeApr = (((_24Vol * _24Fee) / tvl) * 365 * 100)

        # for analytics in _24VolList:
        #     _24Vol = float(analytics["txVolumeUSD"])
        #     _24Fees = float(analytics["feesUSD"])
        #     _24Vol += _24Vol
        #     _24Fees += _24Fees


if __name__ == '__main__':
    pools = caculatePoolData()
    print(pools)
