from datetime import datetime, timedelta

DST = 1
London = ("0000", "0900") if DST == 0 else ("0100", "1000")
NewYork = ("0400", "1400") if DST == 0 else ("0500", "1500")
Sydney = ("1300", "2200") if DST == 0 else ("1400", "2300")
Tokyo = ("1500", "2400") if DST == 0 else ("1600", "0100")
customTime = ("0000", "1200") if DST == 0 else ("0100", "1300")
customTime2 = ("0900", "1200") if DST == 0 else ("1000", "1300")

def time_in_range(time_str, start, end):
    time = datetime.strptime(time_str, "%H%M")
    start_time = datetime.strptime(start, "%H%M")
    end_time = datetime.strptime(end, "%H%M")
    return start_time <= time <= end_time

# Define the timeframe and session
timeframe_period = 1530  # Replace with your desired timeframe period (e.g., 15 minutes)

london = time_in_range(str(timeframe_period).zfill(4), *London)
newyork = time_in_range(str(timeframe_period).zfill(4), *NewYork)
c_time = time_in_range(str(timeframe_period).zfill(4), *customTime)
c_time2 = time_in_range(str(timeframe_period).zfill(4), *customTime2)

# Define start and finish date
fromYear = 2020
fromMonth = 1
fromDay = 1
toYear = 2023
toMonth = 12
toDay = 31
start_date = datetime(fromYear, fromMonth, fromDay)
finish_date = datetime(toYear, toMonth, toDay)
datetime.now() <= (london or newyork)

print("London:", london)
print("New York:", newyork)
print("Custom Time:", c_time)
print("Custom Time 2:", c_time2)
print("Time Condition:", time_cond)
