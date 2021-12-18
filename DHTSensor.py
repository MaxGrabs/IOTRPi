import datetime
import time
import board
import adafruit_dht
import mysql.connector
import schedule
from datetime import datetime, timedelta

dhtDevice = adafruit_dht.DHT11(board.D17)


def job():
    x = True
    while x:
        try:
            now = datetime.now()
            current_time = now.strftime("%Y-%m-%d %H:%M:%S")
            print("Current Time =", current_time)
            temperature_c = dhtDevice.temperature
            temperature_f = temperature_c * (9 / 5) + 32
            humidity = dhtDevice.humidity
            print("Temp: {:.1f} F / {:.1f} C    Humidity: {}% "
                .format(temperature_f, temperature_c, humidity))
            mydb = mysql.connector.connect(
            host="iotpython.mysql.database.azure.com",
            user="dmitry@iotpython",
            password="IOTpassword!",
            database="iotpython"
            )
            mycursor = mydb.cursor()
            sql = "INSERT INTO sensor_one_data (date_time, temp_one, humid_one) VALUES (%s, %s, %s)"
            val = (current_time, temperature_c, humidity)
            mycursor.execute(sql, val)
            mydb.commit()
            mycursor.close()
            mydb.close()
            x = False
        except RuntimeError as error:
            print(error.args[0])

schedule.every().hour.at("00:00").do(job)
schedule.every().hour.at("30:00").do(job)
while True:
    schedule.run_pending()
    time.sleep(1)