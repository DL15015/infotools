import json
import time
from datetime import date, timedelta
import requests
# url = "http://16.162.255.226:8000/subgraphs/name/klein/unstable"


pre2WeekTimeStamp = int(time.time()) - (14 * 86400)
pre2Week = (date.today() + timedelta(days=-14)).strftime("%Y-%m-%d")
pre2Week += " 00:00:00"
pre2Week8HTimeStamp =  int(time.mktime(time.strptime(pre2Week,"%Y-%m-%d %H:%M:%S")))

preWeekTimeStamp = int(time.time()) - (7 * 86400)
preWeek = (date.today() + timedelta(days=-7)).strftime("%Y-%m-%d")
preWeek += " 00:00:00"
preWeek8HTimeStamp =  int(time.mktime(time.strptime(preWeek,"%Y-%m-%d %H:%M:%S")))

pre2DayTimeStamp = int(time.time()) - 2 * 86400
befYesterday = (date.today() + timedelta(days=-2)).strftime("%Y-%m-%d")
befYesterday += " 00:00:00"
pre2Day8HTimeStamp = int(time.mktime(time.strptime(befYesterday,"%Y-%m-%d %H:%M:%S")))

preDayTimeStamp = int(time.time()) - 86400
yesterday = (date.today() + timedelta(days=-1)).strftime("%Y-%m-%d")
yesterday += " 00:00:00"
pre8HTimeStamp =  int(time.mktime(time.strptime(yesterday,"%Y-%m-%d %H:%M:%S")))

curDayTimeStamp = int(time.time())
today = (date.today() + timedelta()).strftime("%Y-%m-%d")
today += " 00:00:00"
cur8HTimeStamp =  int(time.mktime(time.strptime(today,"%Y-%m-%d %H:%M:%S")))

print("pre8HTimeStamp",pre8HTimeStamp)
print("cur8HTimeStamp",cur8HTimeStamp)
print("preWeek8HTimeStamp",preWeek8HTimeStamp)
print("pre2Week8HTimeStamp",pre2Week8HTimeStamp)
print("preDayTimeStamp",preDayTimeStamp)
print("pre2DayTimeStamp",pre2DayTimeStamp)
print("pre2Day8HTimeStamp",pre2Day8HTimeStamp)
print("curDayTimeStamp",curDayTimeStamp)

def getOverviewData(url):
    body = """
    query {
      pools{
        tvlUSD
        _24H:analytics(where:{type:"1",timestamp_gte:%d,timestamp_lte:%d},orderBy:timestamp,orderDirection:desc){
              txVolumeUSD
              feesUSD
            }
      }
      tokens{
        symbol
        priceUSD
        analytics(where:{type:"1",timestamp_gte:%d},orderBy:timestamp,orderDirection:desc,first:1){
          priceUSD
        }
      }
    }
    """ % (preDayTimeStamp,curDayTimeStamp,pre2Day8HTimeStamp)
    data = findData(url,body)
    dic = json.loads(data)
    tvl = 0
    txVolume = 0
    tokenDict = {}
    for index in range(len(dic['data']['pools'])):
        pool = dic['data']['pools'][index]
        tvl += float(pool["tvlUSD"])
        pool24H = pool['_24H']
        if pool24H:
            for analytic in pool24H:
                txVolume += float(analytic["txVolumeUSD"])

    for i in range(len(dic['data']['tokens'])):
        token = dic['data']['tokens'][i]
        symbol = token["symbol"]
        tokenDict[symbol] = 0
        analytics = token["analytics"]
        curPrice = float(token["priceUSD"])
        if analytics :
            prePrice = float(analytics[0]["priceUSD"])
            if prePrice != 0 :
                tokenDict[symbol] = (curPrice - prePrice) / (prePrice)
            tokenDict[symbol] = 0
    return tvl,txVolume,tokenDict

def getPoolData(url):
    body = """
        query data{
          pools {
            name
            fee
            tvlUSD
            _24H:analytics(where:{type:"1",timestamp_gt:%d},orderBy:timestamp,orderDirection:desc){
              txVolumeUSD
              tvlUSD
              feesUSD
            } 
            pre24H:analytics(where:{type:"1",timestamp_gt:%d,timestamp_lte:%d},orderBy:timestamp,orderDirection:desc){
              txVolumeUSD
              tvlUSD
              feesUSD
            } 
            preTVL:analytics(where:{type:"1",timestamp_lt:%d},orderBy:timestamp,orderDirection:desc,first:1){
              tvlUSD
            }
            _7Days:analytics(where:{type:"1",timestamp_gt:%d},orderBy:timestamp,orderDirection:desc){
              txVolumeUSD
            }
          }
        }
    """ % (preDayTimeStamp,pre2DayTimeStamp,preDayTimeStamp,cur8HTimeStamp,preWeekTimeStamp)
    data = findData(url,body)
    dic = json.loads(data)
    poolDict = {}
    for i in range(len(dic["data"]["pools"])):
        pool = dic["data"]["pools"][i]
        poolName = pool["name"]
        tvl = float(pool["tvlUSD"])
        fee = float(pool["fee"])
        pool24HList = pool["_24H"]
        prePool24HList = pool["pre24H"]
        pool7DayList = pool["_7Days"]
        curTVL = tvl
        preTVL = 0

        if pool["preTVL"]:
            preTVL = float(pool["preTVL"][0]["tvlUSD"])

        poolDict[poolName] = {
            "TVL":tvl,
            "TVLChange":0,
            "Volume24H":0,
            "VolumeChange":0,
            "Volume7D":0,
            "Fee24H":0,
            "Fee24HChange":0,
            "FeeAPR":0,
            "FeeAPRChange":0
        }
        pool = poolDict[poolName]
        pool["TVLChange"] = getChange(curTVL, preTVL)

        _24HtxVolume,_24HFeesUSD,_24HFeeAPR = 0, 0, 0
        for analytics in pool24HList:
            txVolume = float(analytics['txVolumeUSD'])
            feesUSD = float(analytics['feesUSD'])
            _24HtxVolume += txVolume
            _24HFeesUSD += feesUSD

        if (tvl != 0) & (pool24HList != []):
            _24HTVL = float(pool24HList[0]["tvlUSD"])
            _24HFeeAPR = (((_24HtxVolume * fee ) / _24HTVL) * 365 * 100)
            pool["FeeAPR"] = _24HFeeAPR


        pool["Volume24H"] = _24HtxVolume
        pool["Fee24H"] = _24HFeesUSD

        pre24HTxVolume,pre24HFeesUSD,pre24HFeeAPR = 0,0,0
        for analytics in prePool24HList:
            txVolume = float(analytics['txVolumeUSD'])
            feesUSD = float(analytics['feesUSD'])
            pre24HTxVolume += txVolume
            pre24HFeesUSD += feesUSD

        if (tvl != 0) & (prePool24HList != []):
            pre24HTVL = float(prePool24HList[0]["tvlUSD"])
            pre24HFeeAPR = (((pre24HTxVolume * fee ) / pre24HTVL) * 365 * 100)

        pool["VolumeChange"] = getChange(_24HtxVolume, pre24HTxVolume)

        _7DayTxVolume = 0
        for analytics in pool7DayList:
            txVolume = float(analytics['txVolumeUSD'])
            _7DayTxVolume +=txVolume


        pool["Fee24HChange"] = getChange(_24HFeesUSD,pre24HFeesUSD)
        pool["FeeAPRChange"] = getChange(_24HFeeAPR,pre24HFeeAPR)
        pool["Volume7D"] = _7DayTxVolume

    return poolDict

def getTokenData(url):
    body = """
        query data{
          tokens{
            symbol
            tvlUSD
            priceUSD
            _24H:analytics(where:{type:"1",timestamp_gte:%d,timestamp_lt:%d},orderBy:timestamp,orderDirection:desc){
              tvlUSD
              txVolumeUSD
              feesUSD
            }
            pre24H:analytics(where:{type:"1",timestamp_gte:%d,timestamp_lt:%d},orderBy:timestamp,orderDirection:desc){
              tvlUSD
              txVolumeUSD
              feesUSD
            }
            pre:analytics(where:{type:"2",timestamp_lt:%d},orderBy:timestamp,orderDirection:desc,first:1){
              tvlUSD
              priceUSD
            }
            _7Days:analytics(where:{type:"1",timestamp_gt:%d},orderBy:timestamp,orderDirection:desc){
              txVolumeUSD
            }
            pre7Days:analytics(where:{type:"1",timestamp_gte:%d,timestamp_lt:%d},orderBy:timestamp,orderDirection:desc){
              txVolumeUSD
            }
          }
        }
    """% (preDayTimeStamp,curDayTimeStamp,pre2DayTimeStamp,preDayTimeStamp,cur8HTimeStamp,preWeekTimeStamp,pre2WeekTimeStamp,preWeekTimeStamp)
    data = findData(url,body)
    dic = json.loads(data)
    tokenDict = {}
    for i in range(len(dic["data"]["tokens"])):
        token = dic["data"]["tokens"][i]
        tokenName = token["symbol"]
        tvl = float(token["tvlUSD"])
        price = float(token["priceUSD"])
        curTVL = tvl
        curPrice = price
        preFee24H, preTVL,prePrice, preWeekVolume, curWeekVolume,prePrice, PriceChange = 0, 0, 0, 0, 0, 0, 0

        token24HList = token["_24H"]
        tokenPre24HList = token["pre24H"]
        token7DaysList = token["_7Days"]
        tokenPre7DaysList = token["pre7Days"]

        tokenDict[tokenName] = {
            "Price": price,
            "PriceChange": 0,
            "TVL":tvl,
            "TVLChange":0,
            "Volume24H":0,
            "Volume48H":0,
            "Volume24HChange":0,
            "Volume14D":0,
            "Volume7D":0,
            "Volume7DChange":0,
            "Fee48H":0,
            "Fee24H":0,
            "Fee24HChange":0
        }

        if token["pre"]:
            preTVL = float(token["pre"][0]["tvlUSD"])
            prePrice = float(token["pre"][0]["priceUSD"])

        token = tokenDict[tokenName]

        token["PriceChange"] = getChange(curPrice, prePrice)
        token["TVLChange"] = getChange(curTVL, preTVL)

        _24HtxVolume, _24HFeesUSD = 0, 0
        for analytics in token24HList:
            txVolume = float(analytics['txVolumeUSD'])
            feesUSD = float(analytics['feesUSD'])
            _24TVL = analytics["tvlUSD"]
            _24HtxVolume += txVolume
            _24HFeesUSD += feesUSD

        token["Volume24H"] = _24HtxVolume
        token["Fee24H"] = _24HFeesUSD



        pre24HtxVolume,pre24HFeesUSD = 0,0
        for analytics in tokenPre24HList:
            txVolume = float(analytics['txVolumeUSD'])
            feesUSD = float(analytics['feesUSD'])
            pre24HtxVolume += txVolume
            pre24HFeesUSD += feesUSD


        token["Fee48H"] = pre24HFeesUSD
        token["Volume48H"] = pre24HtxVolume


        token["Fee24HChange"] = getChange(_24HFeesUSD, pre24HFeesUSD)
        token["VolumeChange"] = getChange(_24HtxVolume, pre24HtxVolume)


        _7DayTxVolume = 0
        for analytics in token7DaysList:
            _7DayTxVolume += float(analytics["txVolumeUSD"])

        token["Volume7D"] = _7DayTxVolume

        _14DayTxVolume = 0
        for analytics in tokenPre7DaysList:
            _14DayTxVolume += float(analytics["txVolumeUSD"])

        token["Volume14D"] = _14DayTxVolume

        token["Volume7DChange"] = getChange(_7DayTxVolume,_14DayTxVolume)
        
    for _,token in tokenDict.items():
        if token["Volume48H"] != 0 :
            vol48H = token["Volume48H"]
            vol24H = token["Volume24H"]
            token["Volume24HChange"] = getChange(vol24H,vol48H)
        
        if token["Volume14D"] != 0:
            vol14D = token["Volume14D"]
            vol7D = token["Volume7D"]
            token["Volume7DChange"] = getChange(vol7D,vol14D)

    return tokenDict

def getTransactions(url):
    body = """
            query{
          tx:exchangeEvents(orderBy:timestamp,orderDirection:desc){
            txVolumeUSD
            executor
          }
          add:liquidityEvents(where:{type:"1"},orderBy:timestamp,orderDirection:desc){
            totalValueUSD
            executor
          }
          rem:liquidityEvents(where:{type:"2"},orderBy:timestamp,orderDirection:desc) {
            totalValueUSD
            executor
          }
        }
        """ % ()
    data = findData(url, body)
    dic = json.loads(data)
    txList = dic["data"]["tx"]
    addList = dic["data"]["add"]
    remList = dic["data"]["rem"]
    print("Swap:",txList)
    print("AddLiquidity:",addList)
    print("RemoveLiquidity:",remList)

def findData(url,body):  
    reqBody = {
        "query":body
    }   
    res = requests.post(url=url,json=reqBody)
    return  res.text

def getChange(cur,pre):
    if pre == 0:
        if cur == 0:
            return 0
        return 100
    return (cur - pre) / pre * 100

if __name__ == "__main__":
    url = input("url:")
    if not url:
        # http://18.167.108.129:8000/subgraphs/name/klein/unstable

        # url = "http://16.162.255.226:8000/subgraphs/name/klein/unstable"
        url = "http://18.167.108.129:8000/subgraphs/name/klein/unstable"
    tvl,vol,tokenDict= getOverviewData(url)
    print("Overview:")
    print("TVL:",tvl)
    print("vol:",vol)
    for k,v in tokenDict.items():
        print(k,v)

    print("-" * 99)
    poolDict = getPoolData(url)
    print("poolDict:")
    for k,v in poolDict.items():
        print(k)
        for pk,pv in v.items():
            print(pk,pv)
        print(" ")

    print("-" * 99)
    tokenDict = getTokenData(url)
    for k,v in tokenDict.items():
        print(k)
        for tk,tv in v.items():
            print(tk,tv)
        print(" ")
    getTransactions(url)
    print("End")