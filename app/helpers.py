from datetime import datetime


def encode_to_dt_sl(timestamps): return datetime.strptime(timestamps, "%Y%m%d").strftime("%d %b %Y")

def decode_date_unix(unix_timestamps):pass

def encode_date_unix(timestamps):pass


  


