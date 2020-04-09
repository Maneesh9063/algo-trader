from kiteconnect import KiteConnect
from kiteconnect import KiteTicker
import pandas as pd
import datetime,random
import pickle,math,threading
import time,concurrent.futures

api_key = "c993gnnc130qfi2p"

api_sec = "ast8w78hd3wjtinibrx9md80z9yer8nw"

# to be pasted from console....|||

at = "i5UHgbaseY1A60TJZFdl1j4O5AOx6I1O  "

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
# temp = [177665]
trd_portfolio = pickle.load(open("given.pickle", "rb"))
# trd_portfolio = {177665:{"name":"CIPLA"}}
subscribe = []
sold_holdings = []
c = ["date", "open", "high", "low", "close"]
d = pd.DataFrame(columns=c)
hist = {}


now = datetime.datetime.now()

# t_to = datetime.datetime(now.year,now.month,now.day-2,15,29)
t_to = datetime.datetime(now.year,now.month,now.day+1,now.hour , now.minute)
t_from =  t_to - datetime.timedelta(minutes=15)



# t_from = datetime.datetime(now.year, now.month, now.day-1)
# t_to = datetime.datetime(now.year, now.month, now.day-1, 15, 30)



for i in trd_portfolio:
    subscribe.append(i)
    trd_portfolio[i]["bought"] = False
    trd_portfolio[i]["sold"] = False


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



def counter_order():
    while True:
        try:
            # bought_holdings = pickle.load(open("bought.pickle","rb"))
            c_positions = kite.positions()['net']

            if len(c_positions) > 0:
                n = datetime.datetime.now()
                c_to = datetime.datetime(n.year, n.month, n.day,n.hour,n.minute)
                c_from =  c_to - datetime.timedelta(minutes=15)
                # print("-----------------------------------------------")
                for count,j in enumerate(c_positions):
                    c_quantity = c_positions[count]["quantity"]
                    if c_quantity < 0 and j["product"] == "MIS":
                        i = j["instrument_token"]
                        hist = kite.historical_data(i,c_from,c_to,'minute')
                        c_df = pd.DataFrame(hist)
                        # print(c_from)
                        # print(c_to) 
                        # print(c_df)
                        c_9_ma = c_df["close"][-9:].mean()
                        # c_ltp = kite.ltp(["NSE:"+trd_portfolio[i]['name']])
                        c_name = trd_portfolio[i]['name']
                        # c_positions = kite.positions()['net']
                        # if j["tradingsymbol"] == c_name :
                            
                        c_ltp = c_positions[count]["last_price"]
                        # print(c_name ,c_ltp, c_9_ma ,c_quantity)

                        if c_ltp > c_9_ma:
                            # print(c_name ,c_ltp, c_9_ma ,c_quantity)

                            kite.place_order(variety = kite.VARIETY_REGULAR , exchange = kite.EXCHANGE_NSE, tradingsymbol = c_name,quantity = -c_quantity, product = kite.PRODUCT_MIS , transaction_type = kite.TRANSACTION_TYPE_BUY, order_type = kite.ORDER_TYPE_MARKET)
                            print("exited order" , c_name , datetime.datetime.now())
                            with open("sell_stats.txt","a") as f:
                                co_o = "exited order " +c_name+" "+str(datetime.datetime.now())+ "\n"
                                f.write(co_o)

                            trd_portfolio[i]["sold"] = False
                            c_positions = kite.positions()['net']

        except Exception as e :
            # print(c_name ,c_ltp, c_9_ma ,c_quantity)

            print(e)
            pass    
        
        time.sleep(1)
t = threading.Thread(target=counter_order)
t.start()

# the whole calculation work and buying & selling is done here
lo = 0

def calculate(single_company):
    try:
        global d,lo
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

        if ltp_t > 50 and ltp_t < 1000:
            # print(lo)
            # print(name)

            # print(ltp_t,0.98*open_t , avg_price_t ,name)

            if ltp_t <= 0.99*(open_t) and ltp_t < avg_price_t:

                # print(t_from)
                # print(t_to)
                d = pd.DataFrame(kite.historical_data(inst_of_single_company, t_from, t_to, "minute"))
                # print(d)
                m_l = min(d["low"][-5:])
                # print("last low " ,m_l , low_t ,name)
                if m_l <= low_t:
                    m5_diff = [0]*5
                    ap = 0
                    for i, j in zip(d["high"][-5:], d["low"][-5:]):
                        m5_diff[ap] = (i-j)
                        ap += 1
                        
                    # print("sell")
                    mx_diff = max(m5_diff)
                    hi_l = m5_diff.index(mx_diff)
                    mn_diff = min(m5_diff[hi_l:])
                    # print(d.iloc[hi_l]["low"], low_t , name ,mn_diff , min(m5_diff))
                    if mn_diff == min(m5_diff) and d.iloc[hi_l]["low"] <= low_t:

                        
                        
                        low_l = m5_diff.index(mn_diff)+1
                        t1 = d.iloc[(low_l)+10]["high"] <= (d.iloc[(hi_l +11)]["high"]-(mx_diff*0.4))

                        # print(mx_diff, mn_diff , name)
                        if mx_diff > 2*mn_diff and t1 and not trd_portfolio[inst_of_single_company]["sold"]:
                            
                            print("-----sell signal ", name)

                            # print(d.iloc[-(low_l+1)]["high"] ,d.iloc[-(len(m5_diff)-hi_l)]["high"]-(mx_diff*0.4) ,d.iloc[-(len(m5_diff)-hi_l)]["high"]  , (mx_diff*0.4) )

                            
                            x = 500
                            quantity = round(x/ltp_t)
                            trigger = low_t - 0.05
                            price = price_cal(trigger)
                            
                            try:
                                kite.place_order(variety = kite.VARIETY_REGULAR , exchange = kite.EXCHANGE_NSE, tradingsymbol = name,quantity = quantity, product = kite.PRODUCT_MIS , transaction_type = kite.TRANSACTION_TYPE_SELL, order_type = kite.ORDER_TYPE_SL, trigger_price = trigger, price = price)

                                sold_holdings.append(inst_of_single_company)
                                pickle.dump(sold_holdings,open("sold.pickle","wb"))
                                trd_portfolio[inst_of_single_company]["sold"] = True
                                pickle.dump(trd_portfolio,open("given.pickle","wb"))

                                with open("buy_sats.txt","a") as f:
                                    s_o = "Sold " +name+" "+str(datetime.datetime.now())+ "\n"
                                    f.write(s_o)     

                
                                print("#sold  ", name ,datetime.datetime.now())# , "last low " ,m_l , low_t,"max of heghts , min" ,round(mx_diff,2) , mn_diff , m5_diff)
                                # lo +=1
                                # print(d)
                                # print("last low " ,m_l , low_t ,name)
                                lo += 1

                            except Exception as e :
                                print("---------not sold cause : ", e)
    except Exception as e :
        print("exception occured : " ,e)



s_len = len(subscribe)
h ={}
def on_ticks(ws, ticks):
    t1 = (time.perf_counter())
    t_len = len(ticks)
    # print(t_len)
    mj = 30
    t =[]
    # random.shuffle(ticks)
    for i in ticks:
        h[i["instrument_token"]] = i
    if len(h) == s_len:
        # print(len(h)) 
        for i in h:
            t.append(h[i])
        # for i in h:
        for i in range(mj-1,t_len,mj):
            # calculate(h[i])
            # print(i)
            with concurrent.futures.ThreadPoolExecutor() as ex:
                ex.map(calculate ,t[i-mj:i])
        # i = 0
        # while i < mj:
        #     t = threading.Thread(target=calculate, args=([ticks[i]]))
        #     t.start()
        #     i += 1
        
        

    t_time = round((time.perf_counter() - t1),2)
    print(t_time)
    with open("timer.txt","a") as f:
        f.write(str(mj)+" = "+str(t_time)+" number of results "+str(lo)+ "\n")
        



# def on_ticks(ws, ticks):
#     # global from_, to, d, hist
#     # pol = 0
#     # print(ticks)
#     t1 = (time.perf_counter())
#     # counter_order()
#     t_len = len(ticks)
#     # print(t_len)
#     mj = 0
#     random.shuffle(ticks)

#     for i in ticks:
#     # for i in range(mj-1,t_len,mj):
#         calculate(i)
#         # print(i)
        
#         # i = 0
#         # while i < mj:
#         #     t = threading.Thread(target=calculate, args=([ticks[i]]))
#         #     t.start()
#         #     i += 1
        
#         # with concurrent.futures.ThreadPoolExecutor() as ex:
#             # ex.map(calculate ,ticks[i-mj:i])

#     t_time = round((time.perf_counter() - t1),2)
#     print(t_time)
#     with open("timer_sell.txt","a") as f:
#         f.write(str(mj)+" = "+str(t_time)+" number of results " + str(lo)+ "\n")



# subscribe=[1215745]
def on_connect(ws, response):
    ws.subscribe(subscribe)
    ws.set_mode(ws.MODE_QUOTE, subscribe)

def on_close(ws, code, reason):
    # On connection close stop the event loop.
    # Reconnection will not happen after executing `ws.stop()`
    ws.stop()

kws.on_ticks = on_ticks
kws.on_connect = on_connect
# kws.on_close = on_close
kws.connect()

