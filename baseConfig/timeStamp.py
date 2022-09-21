import time
from datetime import timedelta, datetime


class Timer:
    def __init__(self):
        self.curTimeStamp = int(time.time())  # 当前时间
        self.pre1hTimeStamp = int(time.time()) - 3600  # 1h前的时间
        self.cur0hTimeStamp = int((time.time()) - (time.time() - time.timezone) % 86400)  # 当天0点时间
        self.pre24hTimeStamp = int(time.time()) - 3600 * 24  # 24h前的时间
        self.pre48TimeStamp = int(time.time()) - 3600 * 48  # 48h前的时间
        self.pre7dTimeStamp = int(time.time()) - 3600 * 24 * 7  # 7天前的时间
        self.pre14dTimeStamp = int(time.time()) - 3600 * 24 * 14  # 14天前的时间

        # print("curTimeStamp", self.curTimeStamp)
        # print("pre1hTimeStamp", self.pre1hTimeStamp)
        # print("cur0hTimeStamp", self.cur0hTimeStamp)
        # print("pre24hTimeStamp", self.pre24hTimeStamp)
        # print("pre48TimeStamp", self.pre48TimeStamp)
        # print("pre7dTimeStamp", self.pre7dTimeStamp)
        # print("pre14dTimeStamp", self.pre14dTimeStamp)


def getChangeLate(preData, curData):
    if preData == 0:
        if curData == 0:
            return "%"
        return "100%"
    return (curData - preData) / preData



if __name__ == '__main__':
    timer=Timer()
    print(timer)
