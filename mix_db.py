from kiteconnect import KiteConnect
from kiteconnect import KiteTicker
import pandas as pd
import datetime,os,run
import pickle,math,threading
import time,concurrent.futures


# pahts of variables
path_of_accces_token = os.path.dirname(os.path.realpath(__file__))+"\\access_token.txt"
path_pickle_for_stock_names =  os.path.dirname(os.path.realpath(__file__))+"\\given.pickle"
path_for_buy_stats = os.path.dirname(os.path.realpath(__file__))+"\\buy_stats.txt"
path_for_sell_stats = os.path.dirname(os.path.realpath(__file__))+"\\sell_stats.txt"

# vairables 
api_key = "c993gnnc130qfi2p"
api_sec = "y9gnaz2ga4z11cdslsnbdd54ldqocmsm"
with open(path_of_accces_token,"r") as f:
    at = f.readline()
    # print(at)

trd_portfolio = pickle.load(open(path_pickle_for_stock_names, "rb"))
subscribe = []
refiner_dict ={}
ho = 0
lo = 0

# now = datetime.datetime.now()
# t_to = datetime.datetime(now.year,now.month,now.day,now.hour , now.minute)
# t_from =  t_to - datetime.timedelta(minutes=3)

# these are for testing purpose

# t_from = datetime.datetime(now.year, now.month, now.day-1)
# t_to = datetime.datetime(now.year, now.month, now.day-1, 15, 30)

for i in trd_portfolio:
    subscribe.append(i)
    trd_portfolio[i]["bought"] = False
    trd_portfolio[i]["sold"] = False

# kite connect settings
# subscribe=subscribe[:50]

kite = KiteConnect(api_key=api_key)
kite.set_access_token(at)
kws = KiteTicker(api_key, at)

# Funtions start here

# No need of thinking about the acces token
# if it is invalid it automatically ask's for the requet token

def acces_token_generator():
    global at
    print("[*] Generate access Token : ",kite.login_url())
    request_tkn = input("[*] Enter Your Request Token Here : ")[-32:]
    data = kite.generate_session(request_tkn, api_sec)
    with open(path_of_accces_token,"w") as f:
        f.write(data["access_token"])
    at = data["access_token"]
    print("Your access token is : " , data["access_token"])

# this is used to cath any accestoken exceptions 
kite.session_expiry_hook = acces_token_generator

def hod_price_cal(trigger):
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


def lod_price_cal(trigger):
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


def hod_refiner(single_company):
    global ho
    ltp_t = single_company["last_price"]
    # avg_price_t = single_company["average_price"]
    open_t = single_company["ohlc"]["open"]
    if ltp_t > 20 and ltp_t < 1000 and ltp_t >= 1.01*(open_t):# and ltp_t > avg_price_t:
        
        try:
            ho +=1
            now = datetime.datetime.now()
            # t_to = datetime.datetime(now.year,now.month,now.day,now.hour , now.minute)
            t_to = datetime.datetime(now.year,now.month,now.day-1,15 , 10)

            t_from =  t_to - datetime.timedelta(minutes=1,)
            if now.second > 0:
                inst_of_single_company = single_company['instrument_token']
                name = trd_portfolio[inst_of_single_company]['name']
                # print(single_company,name)
                ltp_t = single_company["last_price"]
                high_t = single_company["ohlc"]["high"]

                d = (run.historical_data(inst_of_single_company, t_from, t_to, "minute"))
                
                
                # print(d)
                value_pervious_candle_low = d.iloc[-2]["low"]
                value_current_candle_low = d.iloc[-1]["low"]

                value_pervious_candle_high = d.iloc[-2]["high"]
                # value_current_candle_high = d.iloc[-1]["high"]


                if value_current_candle_low > value_pervious_candle_low:

                    if value_pervious_candle_high >= high_t :

                        # print("buy ",name ,value_pervious_candle_high , high_t , datetime.datetime.now())

                        pervious_candle_height = d.iloc[-2]["high"] -d.iloc[-2]["low"]
                        current_candle_height = d.iloc[-1]["high"] -d.iloc[-1]["low"]
                        
                        #  value_current_candle_high != value_current_candle_low and
                        if pervious_candle_height >= current_candle_height*2:

                            if  not trd_portfolio[inst_of_single_company]["bought"]:
                                
                                print("-----buy signal ", name , datetime.datetime.now())

                                return True
        except Exception as e :
            print("exception occured : ",name ,e)
            return False

    else:
        return False


def lod_refiner(single_company):
    global lo
    ltp_t = single_company["last_price"]
    # avg_price_t = single_company["average_price"]
    open_t = single_company["ohlc"]["open"]
    if ltp_t > 20 and ltp_t < 1000 and ltp_t <= 0.99*(open_t):# and ltp_t < avg_price_t:
        global lo
        try:
            lo +=1
            now = datetime.datetime.now()
            # t_to = datetime.datetime(now.year,now.month,now.day,now.hour , now.minute)
            t_to = datetime.datetime(now.year,now.month,now.day-1,15 , 10)
            t_from =  t_to - datetime.timedelta(minutes=1)
            if now.second > 0:
                inst_of_single_company = single_company['instrument_token']
                name = trd_portfolio[inst_of_single_company]['name']
                ltp_t = single_company["last_price"]
                low_t = single_company["ohlc"]["low"]
                

                d = run.historical_data(inst_of_single_company, t_from, t_to, "minute")

                value_pervious_candle_high = d.iloc[-2]["high"]
                value_current_candle_high = d.iloc[-1]["high"]

                value_pervious_candle_low = d.iloc[-2]["low"]
                # value_current_candle_low =  d.iloc[-1]["low"]

                
                if value_current_candle_high < value_pervious_candle_high :
                    
                    # print("sell ",name )

                    if value_pervious_candle_low <= low_t: # and 
                        pervious_candle_height = d.iloc[-2]["high"] -d.iloc[-2]["low"]
                        current_candle_height = d.iloc[-1]["high"] -d.iloc[-1]["low"]

                        # value_current_candle_high != value_current_candle_low and 

                        # print("sell ",name )

                        if pervious_candle_height >=current_candle_height*2:
                    
                        
                            if not trd_portfolio[inst_of_single_company]["sold"]:
                                print("-----sell signal ", name , datetime.datetime.now())
                # print(d)

                                return True

        except Exception as e :
            print("exception occured : ",name ,e)
            return False
        
    else:
        return False


def lod_calculate(single_company):
    global lo
    inst_of_single_company = single_company['instrument_token']
    name = trd_portfolio[inst_of_single_company]['name']
    ltp_t = single_company["last_price"]
    low_t = single_company["ohlc"]["low"]
    # try:
    #     lo +=1
    #     now = datetime.datetime.now()
    #     # t_to = datetime.datetime(now.year,now.month,now.day,now.hour , now.minute)
    #     t_to = datetime.datetime(now.year,now.month,now.day,15 , 10)

    #     t_from =  t_to - datetime.timedelta(minutes=1)
    #     if now.second > 40:
    #         inst_of_single_company = single_company['instrument_token']
    #         name = trd_portfolio[inst_of_single_company]['name']
    #         ltp_t = single_company["last_price"]
    #         low_t = single_company["ohlc"]["low"]
            

    #         d = run.historical_data(inst_of_single_company, t_from, t_to, "minute")

    #         # print(d)
    #         value_pervious_candle_high = d.iloc[-2]["high"]
    #         value_current_candle_high = d.iloc[-1]["high"]

    #         value_pervious_candle_low = d.iloc[-2]["low"]
    #         # value_current_candle_low =  d.iloc[-1]["low"]

            
    #         if value_current_candle_high < value_pervious_candle_high :
                
    #             # print("sell ",name )

    #             if value_pervious_candle_low <= low_t: # and 
    #                 pervious_candle_height = d.iloc[-2]["high"] -d.iloc[-2]["low"]
    #                 current_candle_height = d.iloc[-1]["high"] -d.iloc[-1]["low"]

    #                 # value_current_candle_high != value_current_candle_low and 

    #                 # print("sell ",name )

    #                 if pervious_candle_height >=current_candle_height*2:
                
                    
    #                     if not trd_portfolio[inst_of_single_company]["sold"]:
    #                         print("-----sell signal ", name , datetime.datetime.now()) 
    x = 500
    quantity = round(x/ltp_t)
    trigger = low_t - 0.05
    price = lod_price_cal(trigger)
    # print(quantity)
    print(name)
    # print(d)
    try:
        trd_portfolio[inst_of_single_company]["sold"] = True

        ord_id = 0
        ord_id = kite.place_order(variety = kite.VARIETY_REGULAR , exchange = kite.EXCHANGE_NSE, tradingsymbol = name,quantity = quantity, product = kite.PRODUCT_MIS , transaction_type = kite.TRANSACTION_TYPE_SELL, order_type = kite.ORDER_TYPE_SL, trigger_price = trigger, price = price)


        # with open(path_for_sell_stats,"a") as f:
        #     s_o = "Sold "+str(ord_id)+" " +name+" "+str(datetime.datetime.now())+ "\n"
        #     f.write(s_o) 
        # 
        print("#sold  "+str(ord_id)  , name ,datetime.datetime.now())
        
        
    except Exception as e :
        print("---------not sold cause : ", e)
        with open(path_for_sell_stats,"a") as f:
            s_o = "not Sold " +name+" "+str(datetime.datetime.now())+str(e)+ "\n"
            f.write(s_o) 

    # except Exception as e :
    #     print("exception occured : ",name ,e)


def hod_calculate(single_company):
    global ho
    ltp_t = single_company["last_price"]
    high_t = single_company["ohlc"]["high"]
    inst_of_single_company = single_company['instrument_token']
    name = trd_portfolio[inst_of_single_company]['name']


    # try:
    #     ho +=1
    #     now = datetime.datetime.now()
    #     t_to = datetime.datetime(now.year,now.month,now.day,15 , 10)
    #     t_from =  t_to - datetime.timedelta(minutes=1)
    #     if now.second > 40:
    #         inst_of_single_company = single_company['instrument_token']
    #         name = trd_portfolio[inst_of_single_company]['name']
    #         # print(single_company,name)
    #         ltp_t = single_company["last_price"]
    #         high_t = single_company["ohlc"]["high"]

    #         d = (run.historical_data(inst_of_single_company, t_from, t_to, "minute"))
            
            
            
    #         value_pervious_candle_low = d.iloc[-2]["low"]
    #         value_current_candle_low = d.iloc[-1]["low"]

    #         value_pervious_candle_high = d.iloc[-2]["high"]
    #         # value_current_candle_high = d.iloc[-1]["high"]


    #         if value_current_candle_low > value_pervious_candle_low:

    #             if value_pervious_candle_high >= high_t :

    #                 # print("buy ",name ,value_pervious_candle_high , high_t , datetime.datetime.now())

    #                 pervious_candle_height = d.iloc[-2]["high"] -d.iloc[-2]["low"]
    #                 current_candle_height = d.iloc[-1]["high"] -d.iloc[-1]["low"]
                    
    #                 #  value_current_candle_high != value_current_candle_low and
    #                 if pervious_candle_height >= current_candle_height*2:

    #                     if  not trd_portfolio[inst_of_single_company]["bought"]:
                            
    #                         print("-----buy signal ", name , datetime.datetime.now())

    x = 500
    quantity = round(x/ltp_t)
    trigger = high_t + 0.05
    price = hod_price_cal(trigger)
    print(name)
    # print(d)
    try:
        trd_portfolio[inst_of_single_company]["bought"] = True

        ord_id = 0

        ord_id = kite.place_order(variety = kite.VARIETY_REGULAR , exchange = kite.EXCHANGE_NSE, tradingsymbol = name,quantity = quantity, product = kite.PRODUCT_MIS , transaction_type = kite.TRANSACTION_TYPE_BUY, order_type = kite.ORDER_TYPE_SL, trigger_price = trigger, price = price)

        # with open(path_for_buy_stats,"a") as f:
        #     b_o = "Bought "+str(ord_id) +" "+name+" "+str(datetime.datetime.now())+ "\n"
        #     f.write(b_o)

        print("#bought  "+str(ord_id)  , name ,datetime.datetime.now())
        
        
    except Exception as e :
        print("---------not bought cause : ", e)
        with open(path_for_buy_stats,"a") as f:
            s_o = "not Bought " +name+" "+str(datetime.datetime.now())+str(e)+ "\n"
            f.write(s_o) 
    # except Exception as e :
    #     print("exception occured : ",name ,e)

subscibe_len = len(subscribe)
number_of_threads = 3

print(datetime.datetime.now())
def on_ticks(ws, ticks):
    global refiner_dict,ho,lo
    time_counter_for_ticks = (time.process_time())
    refined_ticks_hod =[]
    refined_ticks_lod =[]
    
    if datetime.datetime.now().time().second >= 0 :
        # print(len(refiner_dict))
        print(len(ticks) , datetime.datetime.now())
        
        for i in ticks:
            time_counter_for_ticks1 = (time.process_time())

            if hod_refiner(i):
                refined_ticks_hod.append(i)
            elif lod_refiner(i):
                refined_ticks_lod.append(i)
            print("t1 ",(time.process_time() - time_counter_for_ticks1))       

        print("loorp ",(time.process_time() - time_counter_for_ticks))       
        ticks_len_hod = (len(refined_ticks_hod))
        ticks_len_lod = (len(refined_ticks_lod))

        print("buy len ",ticks_len_hod)
        print("sell len ",ticks_len_lod)

        # for i in range(0,ticks_len_hod,number_of_threads):
        for i in range(0,ticks_len_hod):
            # time_counter_for_ticks1 = (time.process_time())

            tr = threading.Thread(target=hod_calculate ,args=(refined_ticks_hod[i],))
            tr.start()
            
            # with concurrent.futures.ThreadPoolExecutor() as ex:
            #     ex.map(hod_calculate ,refined_ticks_hod[i:i+number_of_threads])
            # print("t1 ",(time.process_time() - time_counter_for_ticks1))       
        print("t3 ",(time.process_time() - time_counter_for_ticks))       
        
        # for i in range(0,ticks_len_lod,number_of_threads):
        for i in range(0,ticks_len_lod):
        
            tr = threading.Thread(target=lod_calculate,args=(refined_ticks_lod[i],))
            tr.start()
            # with concurrent.futures.ThreadPoolExecutor() as ex:
            #     ex.map(lod_calculate ,refined_ticks_lod[i:i+number_of_threads])
        print("t2 ",(time.process_time() - time_counter_for_ticks))       
        
        print("ho ",ho)
        print("lo ",lo)

        lo,ho = 0,0
        total_time = (time.process_time() - time_counter_for_ticks)
        print("Total ",total_time)
    # total_time = (time.process_time() - time_counter_for_ticks)
    # print(total_time)
    ws.set_mode(ws.MODE_QUOTE, subscribe)


def on_connect(ws, response):
    ws.subscribe(subscribe)
    ws.set_mode(ws.MODE_QUOTE, subscribe)

kws.on_ticks = on_ticks
kws.on_connect = on_connect
kws.connect()

