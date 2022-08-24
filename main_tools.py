import http
import json
import string
import time
from datetime import date, timedelta
import requests

# url = "http://16.162.255.226:8000/subgraphs/name/klein/unstable"

pre2WeekTimeStamp = int(time.time()) - (14 * 86400)
pre2Week = (date.today() + timedelta(days=-14)).strftime("%Y-%m-%d")
pre2Week += " 08:00:00"
pre2Week8HTimeStamp = int(time.mktime(time.strptime(pre2Week, "%Y-%m-%d %H:%M:%S")))

preWeekTimeStamp = int(time.time()) - (7 * 86400)
preWeek = (date.today() + timedelta(days=-7)).strftime("%Y-%m-%d")
preWeek += " 08:00:00"
preWeek8HTimeStamp = int(time.mktime(time.strptime(preWeek, "%Y-%m-%d %H:%M:%S")))

pre2DayTimeStamp = int(time.time()) - 2 * 86400
befYesterday = (date.today() + timedelta(days=-2)).strftime("%Y-%m-%d")
befYesterday += " 08:00:00"
pre8HTimeStamp = int(time.mktime(time.strptime(befYesterday, "%Y-%m-%d %H:%M:%S")))

preDayTimeStamp = int(time.time()) - 86400
yesterday = (date.today() + timedelta(days=-1)).strftime("%Y-%m-%d")
yesterday += " 08:00:00"
pre8HTimeStamp = int(time.mktime(time.strptime(yesterday, "%Y-%m-%d %H:%M:%S")))

curDayTimeStamp = int(time.time())
today = (date.today() + timedelta()).strftime("%Y-%m-%d")
today += " 08:00:00"
cur8HTimeStamp = int(time.mktime(time.strptime(today, "%Y-%m-%d %H:%M:%S")))

print("pre8HTimeStamp", pre8HTimeStamp)
print("cur8HTimeStamp", cur8HTimeStamp)
print("pre2Week8HTimeStamp", pre2Week8HTimeStamp)
print("cur8HTimeStamp", cur8HTimeStamp)
print("preDayTimeStamp", preDayTimeStamp)


def getOverviewData(url):
    body = """
    query pools {
        pools{
            totalValueLockedUSD
        }
        exchanges(where:{timestamp_gt:%d}){
            amountSoldUSD
            amountBoughtUSD
        }        
        tokens{
            symbol
            ethPriceUSD
            dayData(where:{date:%d},orderBy:date,orderDirection:desc,first:1){
            date
            priceUSD
            }
        }
    }
    """ % (preDayTimeStamp, pre8HTimeStamp)
    data = findData(url, body)
    print(data)
    dic = json.loads(data)

    tvl = 0
    print(dic)
    for i in range(len(dic['data']['pools'])):
        totalValueLockedUSD = float(dic['data']['pools'][i]["totalValueLockedUSD"])
        tvl += totalValueLockedUSD

    volume = 0
    for i in range(len(dic['data']['exchanges'])):
        amountSoldUSD = float(dic['data']['exchanges'][i]["amountSoldUSD"])
        amountBoughtUSD = float(dic['data']['exchanges'][i]["amountBoughtUSD"])
        volume += (amountSoldUSD + amountBoughtUSD)

    tokenDict = {}
    for i in range(len(dic['data']['tokens'])):
        token = dic['data']['tokens'][i]
        symbol = token["symbol"]
        tokenDict[symbol] = 0
        tokenDayData = token["dayData"]
        curPrice = float(token["ethPriceUSD"])
        if tokenDayData:
            prePrice = float(tokenDayData[0]["priceUSD"])
            tokenDict[symbol] = (curPrice - prePrice) / (prePrice)

    return tvl, volume, tokenDict


def getPoolData(url):
    body = """
        query data {
            pools{
                name
                totalValueLockedUSD
                fee
                dayData(where:{date_gte:%d,date_lte:%d},orderBy:date,orderDirection:asc,first:2){
                    date
                    tvlUSD
                    volumeUSD
                }
                exchanges(where:{timestamp_gte:%d,timestamp_lte:%d},orderBy:timestamp,orderDirection:asc){
                    totalValueUSD
                    timestamp
                    feesUSD
                }
            }
        }
    """ % (pre8HTimeStamp, cur8HTimeStamp, pre2DayTimeStamp, curDayTimeStamp)
    data = findData(url, body)
    dic = json.loads(data)
    poolDict = {}
    for i in range(len(dic["data"]["pools"])):
        pool = dic["data"]["pools"][i]
        poolName = pool["name"]
        tvl = float(pool["totalValueLockedUSD"])
        curTVL = tvl
        fee = float(pool["fee"])
        poolDayData = pool["dayData"]
        exchanges = pool["exchanges"]
        poolDict[poolName] = {
            "TVl": tvl,
            "TVLchange": 0,
            "Volume24H": 0,
            "VolumeChange": 0,
            "Fee24H": 0,
            "Fee24HChange": 0,
            "FeeAPR": 0,
            "FeeAPRChange": 0
        }
        pool = poolDict[poolName]
        preFeeAPR, preFee24H, curFee24H, preTVL, curVolume24H, preVolume24H = 0, 0, 0, 0, 0, 0
        for exchange in exchanges:
            if int(exchange["timestamp"]) >= int(preDayTimeStamp):
                curFee24H += float(exchange["feesUSD"])
                pool["Fee24H"] = curFee24H
                curVolume24H += float(exchange["totalValueUSD"])
                pool["Volume24H"] = curVolume24H

            if int(exchange["timestamp"]) <= int(preDayTimeStamp):
                preVolume24H += float(exchange["totalValueUSD"])
                preFee24H += float(exchange["feesUSD"])

        if preVolume24H != 0:
            preFeeAPR = (((preVolume24H * fee) / tvl) * 365 * 100)
        if tvl != 0:
            curFeeAPR = (((curVolume24H * fee) / tvl) * 365 * 100)
            pool["FeeAPR"] = curFeeAPR

        if preFeeAPR != 0:
            pool["FeeAPRChange"] = getChange(curFeeAPR, preFeeAPR)

        if preVolume24H != 0:
            pool["VolumeChange"] = getChange(curVolume24H, preVolume24H)

        if preFee24H != 0:
            pool["Fee24HChange"] = getChange(curFee24H, preFee24H)

        for data in poolDayData:
            if int(data["date"]) == int(pre8HTimeStamp):
                preTVL = float(data["tvlUSD"])

            if int(data["date"]) == int(cur8HTimeStamp):
                if preTVL != 0:
                    pool["TVLchange"] = getChange(curTVL, preTVL)

    return poolDict


def getTokenData(url):
    body = """
        query data {
            tokens:tokens{
                symbol        
                totalValueLockedUSD
                dayData(where:{date_gte:%d,date_lte:%d},orderBy:date,orderDirection:asc){
                    date
                    totalValueLocked
                    }
            }
            exchanges:exchanges(where:{timestamp_gte:%d,timestamp_lte:%d},orderBy:timestamp,orderDirection:asc){
                    tokenSold{
                        symbol                    
                    }
                    amountSoldUSD
                    tokenBought{
                        symbol
                    }
                    amountBoughtUSD
                    timestamp
                    feesUSD
                }
        }
    """ % (pre8HTimeStamp, cur8HTimeStamp, pre2Week8HTimeStamp, curDayTimeStamp)
    data = findData(url, body)
    dic = json.loads(data)
    tokenDict = {}
    for i in range(len(dic["data"]["tokens"])):
        token = dic["data"]["tokens"][i]
        tokenName = token["symbol"]
        tvl = float(token["totalValueLockedUSD"])
        curTVL = tvl
        tokenDayData = token["dayData"]
        tokenDict[tokenName] = {
            "TVL": tvl,
            "TVLchange": 0,
            "Volume24H": 0,
            "Volume48H": 0,
            "Volume24HChange": 0,
            "Volume14D": 0,
            "Volume7D": 0,
            "Volume7DChange": 0,
            "Fee48H": 0,
            "Fee24H": 0,
            "Fee24HChange": 0
        }
        token = tokenDict[tokenName]
        preFee24H, preTVL, preWeekVolume, curWeekVolume = 0, 0, 0, 0

        for data in tokenDayData:
            if int(data["date"]) == int(pre8HTimeStamp):
                preTVL = float(data["totalValueLocked"])
                # preVolume = float(data["volumeUSD"])
                # preFee24H = float(data["feesUSD"])

            if int(data["date"]) == int(cur8HTimeStamp):
                # curVolume = float(data["volumeUSD"])
                # curFee24H = float(data["feesUSD"])
                # token["Volume24H"] = curVolume
                # if preVolume != 0:
                #     token["VolumeChange"] = getChange(curVolume,preVolume)
                # if preFee24H != 0:                
                #     token["Fee24HChange"] = getChange(curFee24H,preFee24H)
                if preTVL != 0:
                    token["TVLchange"] = getChange(curTVL, preTVL)

    for i in range(len(dic["data"]["exchanges"])):
        exchange = dic["data"]["exchanges"][i]
        exchangeDate = int(exchange["timestamp"])
        tokenSold = exchange["tokenSold"]["symbol"]
        tokenBought = exchange["tokenBought"]["symbol"]
        amountSoldUSD = float(exchange["amountSoldUSD"])
        amountBoughtUSD = float(exchange["amountBoughtUSD"])
        feesUSD = float(exchange["feesUSD"])

        dictSold = tokenDict[tokenSold]
        dictBought = tokenDict[tokenBought]

        # before 24H 
        if exchangeDate >= int(preDayTimeStamp):
            dictSold["Volume24H"] += amountSoldUSD
            dictBought["Volume24H"] += amountBoughtUSD
            dictSold["Fee24H"] += feesUSD
            dictBought["Fee24H"] += feesUSD

        # before 48H
        if (exchangeDate >= int(pre2DayTimeStamp)) and (exchangeDate < int(preDayTimeStamp)):
            dictSold["Volume48H"] += amountSoldUSD
            dictBought["Volume48H"] += amountBoughtUSD
            dictSold["Fee48H"] += feesUSD
            dictBought["Fee48H"] += feesUSD

        # before 14D                
        if (exchangeDate >= int(pre2Week8HTimeStamp)) and (exchangeDate < int(preWeek8HTimeStamp)):
            dictSold["Volume14D"] += amountSoldUSD
            dictBought["Volume14D"] += amountBoughtUSD

        # before 7D
        if exchangeDate >= int(preWeek8HTimeStamp):
            dictSold["Volume7D"] += amountSoldUSD
            dictBought["Volume7D"] += amountBoughtUSD

    for _, token in tokenDict.items():
        if token["Volume48H"] != 0:
            vol48H = token["Volume48H"]
            vol24H = token["Volume24H"]
            token["Volume24HChange"] = getChange(vol24H, vol48H)

        if token["Volume14D"] != 0:
            vol14D = token["Volume14D"]
            vol7D = token["Volume7D"]
            token["Volume7DChange"] = getChange(vol7D, vol14D)

        if token["Fee48H"] != 0:
            fee24H = token["Fee24H"]
            fee48H = token["Fee48H"]
            token["Fee24HChange"] = getChange(fee24H, fee48H)

    return tokenDict


def findData(url, body):
    reqBody = {
        "query": body
    }
    res = requests.post(url=url, json=reqBody)
    return res.text


def getChange(cur, pre):
    return (cur - pre) / pre * 100


if __name__ == "__main__":
    url = input("url:")
    if not url:
        # url = "http://16.162.255.226:8000/subgraphs/name/klein/unstable"
        url = "http://18.167.108.129:8000/subgraphs/name/klein/unstable"
    tvl, vol, tokenDict = getOverviewData(url)
    print("Overview:")
    print("TVL:", tvl)
    print("vol:", vol)
    for k, v in tokenDict.items():
        print(k, v)

    print("-" * 99)
    poolDict = getPoolData(url)
    print("poolDict:")
    for k, v in poolDict.items():
        print(k)
        for pk, pv in v.items():
            print(pk, pv)
        print(" ")
    # print(poolDict)

    print("-" * 99)
    tokenDict = getTokenData(url)
    print("tokenDict:")
    for k, v in tokenDict.items():
        print(k)
        for tk, tv in v.items():
            print(tk, tv)
        print(" ")
    # print(tokenDict)
    input()
