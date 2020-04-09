from kiteconnect import KiteConnect
from kiteconnect import KiteTicker
import pandas as pd
import datetime
import pickle,math
import time,concurrent.futures

api_key = "c993gnnc130qfi2p"

api_sec = "ast8w78hd3wjtinibrx9md80z9yer8nw"

# to be pasted from console....|||

at = "DnKrTjb2CxgOdyBYHI0hzzz4VCyGkKp7"

kite = KiteConnect(api_key=api_key)

# on time------->>>>>>>>>>>>>
# print("[*] Generate access Token : ",kite.login_url())
# request_tkn = input("[*] Enter Your Request Token Here : ")[-32:]
# # data = kite.generate_session(request_tkn, asecret)
# at = data["access_token"]
# # print(data["access_token"])
# -------------------<<<<<<<<<<<
kite.set_access_token(at)
kws = KiteTicker(api_key, at)

trd_portfolio = pickle.load(open("given.pickle", "rb"))

subscribe = []
bought_holdings = []
sold_holdings = []
for i in trd_portfolio:
    subscribe.append(i)
    trd_portfolio[i]["bought"] = True
    trd_portfolio[i]["sold"] = True

def price_cal(trigger):
    trigger *= 0.999
    p = round(trigger,2)
    frac = round((p - math.floor(p)),2)
    p = (p-frac)
    frac = frac*100

    b = frac%10
    a = math.floor(frac/10)*10
    if(b<5 and b!=0):
        b=0
    elif b == 0:
        b=0
    else:
        b=5
    frac = (a+b)/100
    p = p+frac
    return p

# the whole calculation work and buying & selling is done here
def calculate(single_company):
    inst_of_single_company = single_company['instrument_token']
    name = trd_portfolio[inst_of_single_company]['name']
    # print(single_company,name)
    ltp_t = single_company["last_price"]
    avg_price_t = single_company["average_price"]
    open_t = single_company["ohlc"]["open"]
    high_t = single_company["ohlc"]["high"]
    low_t = single_company["ohlc"]["low"]
    close_t = single_company["ohlc"]["close"]
    print(name)
    if ltp_t > 50 and ltp_t < 500:

        # BUY logic

        if ltp_t >= 1.01*(open_t) and ltp_t > avg_price_t:
            h_data_1m = pd.DataFrame(kite.historical_data(
                inst_of_single_company, t_from, t_to, "minute"))
            # print(t_from , "from")
            # print(t_to , "to")
            # print(h_data_1m)
            d = d.append(h_data_1m)
            #   print(d)
            m_h = max(d["high"][-5:])
            #   print(m_h)
            if m_h >= high_t:
                m5_diff = []
                for i, j in zip(d["high"][-5:], d["low"][-5:]):
                    m5_diff.append(i-j)
                #   print("buy")
                if max(m5_diff) > 2*min(m5_diff) and trd_portfolio[inst_of_single_company]["bought"]:
                    print("buy ", name)
                    trd_portfolio[inst_of_single_company]["bought"] = False


                    x = 2500
                    quantity = round(x/ltp_t)
                    trigger = high_t + 0.05
                    price = price_cal(trigger)

                    print("buy ", name)
                    trd_portfolio[inst_of_single_company]["bought"] = False
                    # kite.place_order(variety = kite.VARIETY_REGULAR , exchange = kite.EXCHANGE_NSE, tradingsymbol = name,quantity = quantity, product = kite.PRODUCT_MIS , transaction_type = kite.TRANSACTION_TYPE_BUY, order_type = kite.ORDER_TYPE_SL, trigger_price = trigger , price = price)
                    bought_holdings.append(inst_of_single_company)

            #sell logic 

        elif ltp_t <= 0.99*(open_t) and ltp_t < avg_price_t:
            h_data_1m = pd.DataFrame(kite.historical_data(
                inst_of_single_company, t_from, t_to, "minute"))
            d = d.append(h_data_1m)
            #   print(d)
            m_l = min(d["low"][-5:])
            #   print(m_l)
            if m_l <= low_t:
                m5_diff = []
                for i, j in zip(d["high"][-5:], d["low"][-5:]):
                    m5_diff.append(i-j)
                #   print("buy")
                if max(m5_diff) > 2*min(m5_diff) and trd_portfolio[inst_of_single_company]["sold"]:
                    print("sell ", name)
                    trd_portfolio[inst_of_single_company]["sold"] = False

                    x = 2500
                    quantity = round(x/ltp_t)
                    trigger = high_t + 0.05
                    price = price_cal(trigger)
                    
                    kite.place_order(variety = kite.VARIETY_REGULAR , exchange = kite.EXCHANGE_NSE, tradingsymbol = name,quantity = quantity, product = kite.PRODUCT_MIS , transaction_type = kite.TRANSACTION_TYPE_SELL, order_type = kite.ORDER_TYPE_SL, trigger_price = trigger, price = price)
                    sold_holdings.append(inst_of_single_company)


now = datetime.datetime.now()

# t_to = datetime.datetime(now.year,now.month,now.day+1,now.hour , now.minute)
# t_from =  t_to -datetime.timedelta(minutes=15)



t_from = datetime.datetime(now.year, now.month, now.day-1)
t_to = datetime.datetime(now.year, now.month, now.day-1, 15, 30)



c = ["date", "open", "high", "low", "close", "sma_20"]
d = pd.DataFrame(columns=c)
hist = {}

def on_ticks(ws, ticks):
    global from_, to, d, hist
    # pol = 0
    print(ticks)
    t1 = (time.perf_counter())
    # with concurrent.futures.ThreadPoolExecutor() as ex:
    #     ex.map(calculate , ticks)
    print(time.perf_counter() - t1)

    # for single_company in ticks:
    #     pol += 1
    #     calculate(single_company,pol)
        


def on_connect(ws, response):
    ws.subscribe(subscribe)
    ws.set_mode(ws.MODE_QUOTE, subscribe)


kws.on_ticks = on_ticks
kws.on_connect = on_connect
kws.connect()
# c=0
# while True:
#     c += 1
#     if c %2 == 0:
#         kws.close()
#     else:


#     time.sleep(60)



# if ltp >= 1.01*(day_open):
#   buy

# max(pervious 5 1_mincandle) >= latest high--->day's high

# max(previous of 5 1_minute candle's(diff of high and low)) > 2*min(previous of 5 1_minute candle's(diff of high and low))


