import requests
import time
import json

url = "http://16.162.255.226:8000/subgraphs/name/klein/unstable"
bodydata = {
    """query data{
          pools {
            tvlUSD
            name
            fee
            tvlUSD
            _24H:analytics(where:{type:"1",timestamp_gte:1662618409,timestamp_lt:1662704809},orderBy:timestamp,orderDirection:desc){
              txVolumeUSD
              tvlUSD
              feesUSD
            }
            _48H:analytics(where:{type:"1",timestamp_gte:1662532009,timestamp_lt:1662618409},orderBy:timestamp,orderDirection:desc){
              txVolumeUSD
              tvlUSD
              feesUSD
            }
            # preTVL:analytics(where:{type:"1",timestamp_lt:%d},orderBy:timestamp,orderDirection:desc,first:1){
            #   tvlUSD
            # }
            # _7Days:analytics(where:{type:"1",timestamp_gt:%d},orderBy:timestamp,orderDirection:desc){
            #   txVolumeUSD
            # }
          }
        }"""
}
res = requests.post(url, json=bodydata)
print(res.json())
print(res.text)
