from datetime import datetime

time_str = "2022-04-05_14:30:00"
time_format = "%Y-%m-%d %H:%M:%S"

try:
    time_obj = datetime.strptime(time_str, time_format)
    print(time_obj)
except ValueError:
    print("err")