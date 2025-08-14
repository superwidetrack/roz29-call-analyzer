#!/usr/bin/env python3

import os
from datetime import datetime, timedelta
import pytz
from dotenv import load_dotenv

load_dotenv()

def debug_time_filtering():
    """Debug the time filtering logic used in get_recent_calls()"""
    print("=== Debugging Time Filtering Logic ===")
    
    # Replicate the exact logic from get_recent_calls() lines 129-132
    MOSCOW_TZ = pytz.timezone('Europe/Moscow')
    time_window_hours = int(os.environ.get("TIME_WINDOW_HOURS", "6"))
    moscow_now = datetime.now(MOSCOW_TZ)
    end_datetime = moscow_now.strftime("%Y-%m-%d %H:%M:%S")
    start_datetime = (moscow_now - timedelta(hours=time_window_hours)).strftime("%Y-%m-%d %H:%M:%S")
    
    print(f"TIME_WINDOW_HOURS: {time_window_hours}")
    print(f"Moscow now: {moscow_now}")
    print(f"Start datetime: {start_datetime}")
    print(f"End datetime: {end_datetime}")
    
    # The recent call we found was at 2025-07-30 20:31:15 MSK
    recent_call_time = datetime(2025, 7, 30, 20, 31, 15)
    recent_call_moscow = MOSCOW_TZ.localize(recent_call_time)
    
    print(f"\nRecent call time: {recent_call_moscow}")
    print(f"Is recent call after start_datetime? {recent_call_moscow >= (moscow_now - timedelta(hours=time_window_hours))}")
    print(f"Is recent call before end_datetime? {recent_call_moscow <= moscow_now}")
    
    # Check if the API parameters are correct
    print(f"\nAPI parameters that would be sent:")
    print(f"start_datetime: {start_datetime}")
    print(f"end_datetime: {end_datetime}")
    
    # The issue might be that we're sending Moscow time to the API but it expects UTC
    print(f"\nPotential issue: API might expect UTC time, not Moscow time")
    moscow_now_utc = moscow_now.astimezone(pytz.UTC)
    start_datetime_utc = (moscow_now_utc - timedelta(hours=time_window_hours)).strftime("%Y-%m-%d %H:%M:%S")
    end_datetime_utc = moscow_now_utc.strftime("%Y-%m-%d %H:%M:%S")
    
    print(f"UTC start_datetime: {start_datetime_utc}")
    print(f"UTC end_datetime: {end_datetime_utc}")
    
    # Check the recent call in UTC
    recent_call_utc = recent_call_moscow.astimezone(pytz.UTC)
    print(f"Recent call in UTC: {recent_call_utc}")

if __name__ == "__main__":
    os.environ["TIME_WINDOW_HOURS"] = "1"
    debug_time_filtering()
