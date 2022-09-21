import json

from baseConfig.GraphQL import Graph
from baseConfig.config import findData
from baseConfig.urls import Urls


def getOverviewData():
    url = input("url:")
    if not url:
        url = Urls.testGraphQLUrl
    res = findData(url=url, body=Graph.overViewQuery)
    res = json.loads(res)
    return res


class Overview:
    def __init__(self, tvlUSD, DayTxVolume):
        self.tvlUSD = tvlUSD
        self.DayTxVolume = DayTxVolume


def calculateOverviewData():
    pools = getOverviewData()
    tvlUSD = 0
    _24HtxVolume = 0
    for index in pools["data"]["pools"]:
        tvlUSD += float(index["tvlUSD"])
        for indes in index["_24prevol"]:
            _24HtxVolume += float(indes["txVolumeUSD"])
    overviewObj = Overview(tvlUSD,_24HtxVolume)
    return overviewObj


if __name__ == '__main__':
    overviewObj = calculateOverviewData()
    print(overviewObj.tvlUSD)
    print(overviewObj.DayTxVolume)
