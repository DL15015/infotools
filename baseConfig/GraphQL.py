from baseConfig.timeStamp import Timer


class Graph():
    timer = Timer()

    overViewQuery = """
   query{
  pools {
    name
    tvlUSD
    _24prevol: analytics(
      where: {type: "1", timestamp_gte: %d, timestamp_lte: %d}
      orderBy: timestamp
      orderDirection: desc
    ) {
      txVolumeUSD
    }
  }
}
   """ % (timer.pre24hTimeStamp, timer.curTimeStamp)

    poolsQuery = """
    query{
      pools {
        name
        tvlUSD
        _0hTvl: analytics(
          where: {type: "1", timestamp_lt: %d}
          orderBy: timestamp
          orderDirection: desc
          first: 1
        ) {
          tvlUSD
        }
        _24Vol: analytics(
          where: {type: "1", timestamp_gte: %d, timestamp_lte: %d}
          orderBy: timestamp
          orderDirection: desc
        ) {
          txVolumeUSD
          tvlUSD
          feesUSD
        }
        _24_48Vol: analytics(
          where: {type: "1", timestamp_gte: %d, timestamp_lte: %d}
          orderBy: timestamp
          orderDirection: desc
        ) {
          txVolumeUSD
          tvlUSD
          feesUSD
        }
        _7dVol: analytics(
          where: {type: "1", timestamp_gte: %d, timestamp_lte: %d}
          orderBy: timestamp
          orderDirection: desc
        ) {
          txVolumeUSD
        }
      }
    }""" % (
        timer.cur0hTimeStamp, timer.pre24hTimeStamp, timer.curTimeStamp, timer.pre48TimeStamp, timer.pre24hTimeStamp,
        timer.pre7dTimeStamp, timer.curTimeStamp)

    tokenQuery = """
        query{
      tokens {
        name
        tvlUSD
        priceUSD
        _pre1hPri: analytics(
          where: {type: "1", timestamp_lt: %d}
          orderBy: timestamp
          orderDirection: desc
          first: 1
        ) {
          priceUSD
        }
        _0hTvl: analytics(
          where: {type: "1", timestamp_lt: %d}
          orderBy: timestamp
          orderDirection: desc
          first: 1
        ) {
          tvlUSD
        }
        _24Vol: analytics(
          where: {type: "1", timestamp_gte: %d, timestamp_lte: %d}
          orderBy: timestamp
          orderDirection: desc
        ) {
          txVolumeUSD
          feesUSD
        }
        _24_48Vol: analytics(
          where: {type: "1", timestamp_gte: %d, timestamp_lte: %d}
          orderBy: timestamp
          orderDirection: desc
        ) {
          txVolumeUSD
          feesUSD
        }
        _7dVol: analytics(
          where: {type: "1", timestamp_gte: %d, timestamp_lte: %d}
          orderBy: timestamp
          orderDirection: desc
        ) {
          txVolumeUSD
        }
        _7d_14dVol: analytics(
          where: {type: "1", timestamp_gte: %d, timestamp_lte: %d}
          orderBy: timestamp
          orderDirection: desc
        ) {
          txVolumeUSD
        }
      }
    }
    """ % (timer.pre1hTimeStamp, timer.cur0hTimeStamp, timer.pre24hTimeStamp, timer.curTimeStamp, timer.pre48TimeStamp,
           timer.pre24hTimeStamp, timer.pre7dTimeStamp, timer.curTimeStamp, timer.pre14dTimeStamp, timer.pre7dTimeStamp)

    transactionQuery="""
        query{
      exchangeEvents(orderBy: timestamp, orderDirection: desc) {
        txVolumeUSD
        tokensSymbol
        amountUSDPair
        executor
      }
      add: liquidityEvents(
        where: {type: "1"}
        orderBy: timestamp
        orderDirection: desc
      ) {
        totalValueUSD
        executor
      }
       rem: liquidityEvents(
        where: {type: "2"}
        orderBy: timestamp
        orderDirection: desc
      ) {
        totalValueUSD
        executor
      }
    }
    """
