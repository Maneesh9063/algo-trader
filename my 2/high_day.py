from kiteconnect import KiteConnect
from kiteconnect import KiteTicker
import pandas as pd
import datetime
import pickle,math,threading
import time,concurrent.futures

api_key = "c993gnnc130qfi2p"

api_sec = "ast8w78hd3wjtinibrx9md80z9yer8nw"

# to be pasted from console....|||

at = "p4u5BZp3glsibdDybT6URI14n5zgeOA8"

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
sold_holdings = {}
sold_holdings = {}

c = ["date", "open", "high", "low", "close"]
d = pd.DataFrame(columns=c)
hist = {}
for i in trd_portfolio:
    subscribe.append(i)
    trd_portfolio[i]["bought"] = True
    trd_portfolio[i]["sold"] = True

def price_cal(trigger):
    trigger *= 1.001
    p = round(trigger,2)
    frac = round((p - math.floor(p)),2)
    p = (p-frac)
    frac = frac*100
    b = frac%10
    a = math.floor(frac/10)*10
    if b <= 5 and b != 0:
        b=5    
    elif(b==0):
        b=0
    else:
        b=10
    frac = (a+b)/100
    p +=frac
    return p


def counter_order():
    if len(sold_holdings) > 0:
        n = datetime.datetime.now()
        c_to = datetime.datetime(n.year, n.month, n.day-1, 15, 30)
        c_from =  c_to -datetime.timedelta(minutes=15)

        # t_from = datetime.datetime(n.year, n.month, n.day-1)
        # t_to = datetime.datetime(n.year, n.month, n.day-1, 15, 30)
        for i in sold_holdings:
            hist = kite.historical_data(i,c_from,c_to,'minute')
            c_df = pd.DataFrame(hist,columns=c) 
            c_9_ma = c_df["close"][-9:].mean()
            # c_ltp = kite.ltp(["NSE:"+trd_portfolio[i]['name']])
            c_name = sold_holdings[i]['name']
            c_positions = kite.positions()['net']

            for i in c_positions:
                if i["trading_symbol"] == c_name:
                    c_quantity = c_positions["quantity"]
                    c_ltp = c_positions["last_price"]
                    if c_ltp < c_9_ma and c_quantity > 0:
                        kite.place_order(variety = kite.VARIETY_REGULAR , exchange = kite.EXCHANGE_NSE, tradingsymbol = c_name,quantity = c_quantity, product = kite.PRODUCT_MIS , transaction_type = kite.TRANSACTION_TYPE_SELL, order_type = kite.ORDER_TYPE_MARKET)
                        del sold_holdings[i]
                    else:
                        del sold_holdings[i]

            

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
    # print(name)

    if ltp_t > 50 and ltp_t < 500:

        # BUY logic

        if ltp_t >= 1.01*(open_t) and ltp_t > avg_price_t:
            h_data_1m = pd.DataFrame(kite.historical_data(
                inst_of_single_company, t_from, t_to, "minute"))
            # print(t_from , "from")
            # print(t_to , "to")
            print(h_data_1m)
            d = d.append(h_data_1m)
            #   print(d)
            m_h = max(d["high"][-5:])
            #   print(m_h)
            if m_h >= high_t:
                m5_diff = []
                for i, j in zip(d["high"][-5:], d["low"][-5:]):
                    m5_diff.append(i-j)
                #   print("buy")
                if max(m5_diff) > 2*min(m5_diff) and not trd_portfolio[inst_of_single_company]["bought"]:
                    
                    x = 2500
                    quantity = round(x/ltp_t)
                    trigger = high_t + 0.05
                    price = price_cal(trigger)

                    print("buy ", name)
                    trd_portfolio[inst_of_single_company]["bought"] = True
                    o_id = kite.place_order(variety = kite.VARIETY_REGULAR , exchange = kite.EXCHANGE_NSE, tradingsymbol = name,quantity = quantity, product = kite.PRODUCT_MIS , transaction_type = kite.TRANSACTION_TYPE_BUY, order_type = kite.ORDER_TYPE_SL, trigger_price = trigger , price = price)
                    sold_holdings[inst_of_single_company] = {"order_id":o_id,"quantity":quantity,"name":name}
            #sell logic 

    
now = datetime.datetime.now()

# t_to = datetime.datetime(now.year,now.month,now.day+1,now.hour , now.minute)
# t_from =  t_to -datetime.timedelta(minutes=15)

t_from = datetime.datetime(now.year, now.month, now.day-1)
t_to = datetime.datetime(now.year, now.month, now.day-1, 15, 30)



def on_ticks(ws, ticks):
    global from_, to, d, hist
    # pol = 0
    # print(ticks)
    t1 = (time.perf_counter())
    with concurrent.futures.ThreadPoolExecutor() as ex:
        ex.map(calculate , ticks)
        ex.map(counter_order)
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
