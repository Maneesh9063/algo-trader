import concurrent.futures
from kiteconnect import KiteConnect
from kiteconnect import KiteTicker
import pandas as pd
import datetime,time,threading
import pickle,math,pprint
import time,concurrent.futures

api_key = "c993gnnc130qfi2p"

api_sec = "y9gnaz2ga4z11cdslsnbdd54ldqocmsm"
kite = KiteConnect(api_key=api_key)

# to be pasted from console....|||

at = "SoBl3q9qX0lYgTxH3CTKGbfALskIwQIg"

# print("[*] Generate access Token : ",kite.login_url())
# request_tkn = input("[*] Enter Your Request Token Here : ")[-32:]
# data = kite.generate_session(request_tkn, api_sec)
# at = data["access_token"]
# print(data["access_token"])



kite.set_access_token(at)
kws = KiteTicker(api_key, at)
c = ["date", "open", "high", "low", "close"]
d = pd.DataFrame(columns=c)



# # now = datetime.datetime.now()

# # t_to = datetime.datetime(now.year,now.month,now.day+1,now.hour , now.minute)
# # t_from =  t_to -datetime.timedelta(minutes=15)


# # print(t_from)
# # print(t_to)
# # h_data_1m = pd.DataFrame(kite.historical_data(177665, t_from, t_to, "minute"))
# # h_data_1m = (kite.historical_data(177665, "2016-02-03" , "2016-02-03", "minute"))
# # d = d.append(h_data_1m)

# # def hi(a,b):
# #     print(a,b)

# # f = [(1,2),(9,7)]
# # with concurrent.futures.ThreadPoolExecutor() as ex:
# #         ex.map(hi , f)

# # s = kite.place_order(variety = kite.VARIETY_REGULAR , exchange = kite.EXCHANGE_NSE, tradingsymbol = "SBIN",quantity = 1, product = kite.PRODUCT_MIS , transaction_type = kite.TRANSACTION_TYPE_BUY, order_type = kite.ORDER_TYPE_SL, trigger_price = 190, price = 191)

# # f= kite.positions()
# # print(f["net"][0])
# # # for i in f:
# # #     print(i["order_id"])
# # # # print(f[0]["order_id"])
# # # c = kite.ltp(["NSE:SBIN"])

# trd_portfolio = pickle.load(open("given.pickle","rb"))



# # for i in trd_portfolio:
# #     # subscribe.append(i)
# #     print(i["name"])
# #     # trd_portfolio[i]["bought"] = False
# #     # trd_portfolio[i]["sold"] = False

# # # print(trd_portfolio)

# pickle.dump(trd_portfolio,open("given.txt","wb"))

# l = ["AUBANK" , "GSPL" , "VGUARD" ,]

# # # pickle.dump(l,open("bought.pickle","wb"))

# # # # del d[d.index(177665)]
# # # for i in d:
# # #     print((i,trd_portfolio[i]["name"] ))

# # print(trd_portfolio)


for i in range(20,3):
    print()