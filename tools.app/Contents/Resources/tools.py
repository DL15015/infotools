import http
import json
import string
import time
from datetime import date, timedelta
import requests

# url = "http://16.162.255.226:8000/subgraphs/name/klein/unstable"

pre2WeekTimeStamp = (int(time.time()) - (14 * 86400))
pre2Week = (date.today() + timedelta(days=-14)).strftime("%Y-%m-%d")
pre2Week += " 08:00:00"
pre2Week8HTimeStamp =  int(time.mktime(time.strptime(pre2Week,"%Y-%m-%d %H:%M:%S")))

preWeekTimeStamp = (int(time.time()) - (7 * 86400))
preWeek = (date.today() + timedelta(days=-7)).strftime("%Y-%m-%d")
preWeek += " 08:00:00"
preWeek8HTimeStamp =  int(time.mktime(time.strptime(preWeek,"%Y-%m-%d %H:%M:%S")))

preDayTimeStamp = (int(time.time()) - 86400)
yesterday = (date.today() + timedelta(days=-1)).strftime("%Y-%m-%d")
yesterday += " 08:00:00"
pre8HTimeStamp =  int(time.mktime(time.strptime(yesterday,"%Y-%m-%d %H:%M:%S")))

curDayTimeStamp = (int(time.time()))
today = (date.today() + timedelta()).strftime("%Y-%m-%d")
today += " 08:00:00"
cur8HTimeStamp =  int(time.mktime(time.strptime(today,"%Y-%m-%d %H:%M:%S")))

# print(cur8HTimeStamp)
# print(pre8HTimeStamp)
# print(preWeek8HTimeStamp)

def getOverviewData(url):
    body = """
    query pools {
        pools{
            totalValueLockedUSD
        }
        exchanges(where:{timestamp_gt:%d}){
            amountSold
            amountBought
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
    """ % (preDayTimeStamp,pre8HTimeStamp)
    data = findData(url,body)
    dic = json.loads(data)

    tvl = 0
    for i in range(len(dic['data']['pools'])):
        totalValueLockedUSD = float(dic['data']['pools'][i]["totalValueLockedUSD"])
        tvl += totalValueLockedUSD
    
    volume = 0
    for i in range(len(dic['data']['exchanges'])):
        amountSold = float(dic['data']['exchanges'][i]["amountSold"])
        amountBought = float(dic['data']['exchanges'][i]["amountBought"])
        volume += (amountSold + amountBought)
    
    tokenDict = {}
    for i in range(len(dic['data']['tokens'])):
        token = dic['data']['tokens'][i]
        symbol = token["symbol"]
        tokenDict[symbol] = 0
        tokenDayData = token["dayData"]
        curPrice = float(token["ethPriceUSD"])
        if tokenDayData :            
            prePrice = float(tokenDayData[0]["priceUSD"])  
            tokenDict[symbol] = (curPrice - prePrice) / (prePrice)
            

    return tvl,volume,tokenDict

def getPoolData(url):
    body = """
        query datas {
            pools{
                name
                totalValueLockedUSD
                fee
                dayData(where:{date_gte:%d,date_lte:%d},orderBy:date,orderDirection:asc,first:2){
                    date
                    tvlUSD
                    volumeUSD
                    feesUSD
                }
            }
        }
    """ % (pre8HTimeStamp,cur8HTimeStamp)
    data = findData(url,body)
    dic = json.loads(data)
    # print(dic)
    poolDict = {} 
    for i in range(len(dic["data"]["pools"])):
        pool = dic["data"]["pools"][i]
        poolName = pool["name"]
        tvl = float(pool["totalValueLockedUSD"])
        curTVL = tvl
        fee = float(pool["fee"])
        poolDayData = pool["dayData"]
        poolDict[poolName] = {
            "TVl":tvl,
            "TVLchange":0,
            "Volume24H":0,
            "VolumeChange":0,
            "Fee24H":0,
            "Fee24HChange":0,
            "FeeAPR":0,
            "FeeAPRChange":0
        }
        preFeeAPR,preVolume,preFee24H,preTVL = 0,0,0,0
        for data in poolDayData:             
            if int(data["date"]) == int(pre8HTimeStamp):
                preTVL = float(data["tvlUSD"])                
                preVolume = float(data["volumeUSD"])
                preFee24H = float(data["feesUSD"])
                if tvl != 0:                    
                    preFeeAPR = (((preVolume * fee ) / tvl) * 365 * 100)                               

            if int(data["date"]) == int(cur8HTimeStamp):                
                feeUSD = float(data["feesUSD"])
                curVolume = float(data["volumeUSD"])
                curFee24H = float(data["feesUSD"])
                poolDict[poolName]["Volume24H"] = curVolume
                poolDict[poolName]["Fee24H"] = feeUSD        
                if tvl != 0:
                    curFeeAPR = (((curVolume * fee ) / tvl) * 365 * 100)
                    poolDict[poolName]["FeeAPR"] = curFeeAPR
                if preFeeAPR != 0:                                               
                    poolDict[poolName]["FeeAPRChange"] = getChange(curFeeAPR,preFeeAPR)
                if preVolume != 0:
                    poolDict[poolName]["VolumeChange"] = getChange(curVolume,preVolume)
                if preFee24H != 0:                
                    poolDict[poolName]["Fee24HChange"] = getChange(curFee24H,curFee24H)
                if preTVL != 0:
                    poolDict[poolName]["TVLchange"] = getChange(curTVL,preTVL)
        
    return poolDict

def getTokenData(url):
    body="""
        query datas {
            tokens{
                symbol        
                totalValueLockedUSD        
                dayData(where:{date_gte:%d ,date_lte:%d},orderBy:date,orderDirection:desc,first:7){
                date
                totalValueLocked
                volumeUSD
      					feesUSD
                }
            }
        }
    """ % (pre2Week8HTimeStamp,cur8HTimeStamp)
    data = findData(url,body)
    dic = json.loads(data)

    tokenDict = {}
    for i in range(len(dic["data"]["tokens"])):
        token = dic["data"]["tokens"][i]
        tokenName = token["symbol"]
        tvl = float(token["totalValueLockedUSD"])
        curTVL = tvl
        tokenDayData = token["dayData"]
        tokenDict[tokenName] = {
            "TVL":tvl,
            "TVLchange":0,
            "Volume24H":0,
            "Volume24HChange":0,
            "Volume7D":0,
            "Volume7DChange":0,
            "Fee24H":0,
            "Fee24HChange":0
        }
        preVolume,preFee24H,preTVL = 0,0,0
        preWeekVolume,curWeekVolume = 0,0
        for data in tokenDayData:
            if int(data["date"]) == int(pre8HTimeStamp):
                preTVL = float(data["totalValueLocked"])
                preVolume = float(data["volumeUSD"])
                preFee24H = float(data["feesUSD"])
            
            if int(data["date"]) == int(cur8HTimeStamp):
                curVolume = float(data["volumeUSD"])
                curFee24H = float(data["feesUSD"])
                tokenDict[tokenName]["Volume24H"] = curVolume
                if preVolume != 0:
                    tokenDict[tokenName]["VolumeChange"] = getChange(curVolume,preVolume)
                if preFee24H != 0:                
                    tokenDict[tokenName]["Fee24HChange"] = getChange(curFee24H,preFee24H)
                if preTVL != 0:
                    tokenDict[tokenName]["TVLchange"] = getChange(curTVL,preTVL)

            if int(data["date"]) <= int(preWeek8HTimeStamp):
                preWeekVolume += float(data["volumeUSD"])
            if int(data["date"]) > int(preWeek8HTimeStamp):
                curWeekVolume += float(data["volumeUSD"])
                tokenDict[tokenName]["Volume7D"] = curWeekVolume
                if preWeekVolume != 0:
                    tokenDict[tokenName]["Volume7DChange"] = getChange(curWeekVolume,preWeekVolume)
    return tokenDict

def findData(url,body):  
    reqBody = {
        "query":body
    }   
    res = requests.post(url=url,json=reqBody)
    return  res.text

def getChange(cur,pre):
    return (cur - pre) / pre * 100

if __name__ == "__main__":
    url = input("url:")
    if not url:
        print("123")
        url = "http://16.162.255.226:8000/subgraphs/name/klein/unstable"
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
    # print(poolDict)
    
    print("-" * 99)
    tokenDict = getTokenData(url)
    print("tokenDict:")
    for k,v in tokenDict.items():
        print(k)
        for tk,tv in v.items():
            print(tk,tv)
        print(" ")
    # print(tokenDict)
    input()