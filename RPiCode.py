# Write your code here :-)
import datetime
import time
import json
import daemon
import board
import adafruit_dht
import requests
#import schedule
import mysql.connector
from datetime import datetime, timedelta
dhtDevice = adafruit_dht.DHT11(board.D17)

def job():
    now = datetime.now()
    y = True
    while y:
        try:
            #get readings
            now = datetime.now()
            current_time = now.strftime("%Y-%m-%d %H:%M:00")
            print("Current Time =", current_time)

            temperature_c = dhtDevice.temperature
            humidity = dhtDevice.humidity

            #post current readings to local
            if humidity is not None and temperature_c is not None:
                print("Temp: {:.1f} C    Humidity: {}% "
                    .format(temperature_c, humidity))

                mydb = mysql.connector.connect(
                host= "localhost",
                user= "dima",
                password= "password",
                database= "dht2db",)

                mycursor = mydb.cursor()
                mycursor.execute("INSERT INTO Sensordata (pi_id, data, data_type, date_time, sentdata) VALUES (1,\'%s\','temperature','%s\', 0)"%(temperature_c,current_time))
                print("saved temperature")

                mycursor.execute("INSERT INTO Sensordata (pi_id, data, data_type, date_time, sentdata) VALUES (1,\'%s\','humidity','%s\', 0)"%(humidity,current_time))
                print("saved humidity")
                mydb.commit()
                mycursor.close()
                mydb.close()
                #end of local Saving
                #post
                y = False
                offlinejob()

        except RuntimeError as error:
            print(error.args[0])
            time.sleep(1.0)
            continue
        except Exception as error:
            dhtDevice.exit()
            print(error.args[0])
            time.sleep(1)
        time.sleep(1)


def offlinejob():
    url = 'https://dmitryg.pythonanywhere.com/data/send'
    urltoken = 'https://dmitryg.pythonanywhere.com/token'
    user = '{"username": "pi1","password": "pi1password"}'
    try:
        mydb = mysql.connector.connect(
            host= "localhost",
            user= "dima",
            password= "password",
            database= "dht2db",)

        mycursor = mydb.cursor(dictionary=True)
        mycursor.execute("SELECT pi_id, data, data_type, date_time  FROM Sensordata WHERE sentdata = 0")
        result = mycursor.fetchall()
        if result is not None:
            #print(result)
            myobj = json.dumps(result)
            print(myobj)
            token = ""
            token_requests = requests.post(urltoken, json=user)
            print(token_requests)
            token_json = token_requests.json()
            for key, value in token_json.items():
                print(key,value)
            token = token_json['token']
            print("token received")
            response = requests.post(url, json=myobj, headers = {"Content-Type" : "application/json","Authorization" : token})
            print("Data sent over successfully")
        #change value to 1 so it's not sent again later on.
        mycursor.execute("UPDATE Sensordata SET sentdata = 1 WHERE sentdata = 0")
        print("Local Database updated, previous records archived")
        mydb.commit()
        mycursor.close()
        mydb.close()
    except (requests.ConnectionError, requests.Timeout) as exception:
        print(e)
        pass;
    except Exception as e:
        print(e)

job()
#old scheduler
#schedule.every(5).seconds.do(job)
#while True:
    #schedule.run_pending()
    #time.sleep(1)