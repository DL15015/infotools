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
        _24VolList = index["_24Vol"]
        _24_48VolList = index["_24_48Vol"]
        _7dVolList = index["_7dVol"]
        _0hTvl = 0

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

        if _0hTvlList:
            for analytics in _0hTvlList:
                _0hTvl = float(analytics["tvlUSD"])


        pool = poolList["poolName"]
        pool["TVLChange"] = getChangeLate(tvl, _0hTvl)
        print(pool)


        _24Vol, _24Fee, _24FeeApr, _24Tvl = 0, 0, 0, 0
        for analytics in _24VolList:
            _24Vol = float(analytics["txVolumeUSD"])
            _24Fee = float(analytics["feesUSD"])
            _24Vol += _24Vol
            _24Fee += _24Fee

            # print(_24VolList)
            # print(analytics)

            # print(_24Vol)
            # print(_24Fee)

        # if (tvl != 0) & (_24VolList != []):
        #     _24Tvl=float(["_24VolList"]["tvlUSD"])
        #     _24FeeApr = (((_24Vol * _24Fee) / tvl) * 365 * 100)
        #     pool["FeeAPR"]=_24FeeApr

        # for analytics in _24VolList:
        #     _24Vol = float(analytics["txVolumeUSD"])
        #     _24Fees = float(analytics["feesUSD"])
        #     _24Vol += _24Vol
        #     _24Fees += _24Fees


if __name__ == '__main__':
    pools = caculatePoolData()
    print(pools)
