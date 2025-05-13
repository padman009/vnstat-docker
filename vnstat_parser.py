import subprocess
import re
from datetime import datetime
import logging
from config import VNSTAT_IFACE, TOP_MIN5_COUNT, LOG_FILE, LOG_LEVEL, LOG_FORMAT

# logging.basicConfig(filename='vnstat_dashboard.log', level=logging.INFO, format='%(asctime)s %(message)s')

def get_vnstat_output(args):
    result = subprocess.run(['vnstat', '-i', VNSTAT_IFACE] + args, capture_output=True, text=True)
    return result.stdout

def parse_5min():
    out = get_vnstat_output(['-5'])
    logging.info(f"[parse_5min] RAW OUTPUT:\n{out}")
    lines = out.splitlines()
    data = []
    current_date = ""
    current_hour = ""
    
    for line in lines:
        date_match = re.match(r"\s*(\d{4}-\d{2}-\d{2})", line)
        if date_match:
            current_date = date_match.group(1)
            continue
            
        hour_match = re.match(r"\s*(\d{2}):00", line)
        if hour_match:
            current_hour = hour_match.group(1)
            continue
            
        m = re.match(
            r"\s*(\d{2}:\d{2})\s+([\d,\.]+)\s+(\w+)\s*\|\s*([\d,\.]+)\s+(\w+)\s*\|\s*([\d,\.]+)\s+(\w+)\s*\|\s*([\d,\.]+)\s+(\w+)",
            line)
        if m and current_date and current_hour:
            minute = m.group(1)
            rx = f"{m.group(2).replace(',', '.')} {m.group(3)}"
            tx = f"{m.group(4).replace(',', '.')} {m.group(5)}"
            total = f"{m.group(6).replace(',', '.')} {m.group(7)}"
            avg = f"{m.group(8).replace(',', '.')} {m.group(9)}"
            data.append({
                'date': current_date,
                'hour': current_hour,
                'minute': minute,
                'rx': rx,
                'tx': tx,
                'total': total,
                'avg': avg
            })
    logging.info(f"[parse_5min] PARSED {len(data)} rows: {data[:3]}")
    if not data:
        logging.warning("[parse_5min] NO DATA PARSED!")
    return data[-TOP_MIN5_COUNT:] if data else []

def parse_hourly():
    out = get_vnstat_output(['-h'])
    logging.info(f"[parse_hourly] RAW OUTPUT:\n{out}")
    lines = out.splitlines()
    data = []
    current_date = ""
    for line in lines:
        m_date = re.match(r"\s*(\d{4}-\d{2}-\d{2})", line)
        if m_date:
            current_date = m_date.group(1)
            continue
        m = re.match(r"\s*(\d{1,2}):00\s+([\d,\.]+)\s+(\w+)\s*\|\s*([\d,\.]+)\s+(\w+)\s*\|\s*([\d,\.]+)\s+(\w+)\s*\|\s*([\d,\.]+)\s+(\w+)", line)
        if m and current_date:
            hour = m.group(1)
            rx = f"{m.group(2).replace(',', '.')} {m.group(3)}"
            tx = f"{m.group(4).replace(',', '.')} {m.group(5)}"
            total = f"{m.group(6).replace(',', '.')} {m.group(7)}"
            avg = f"{m.group(8).replace(',', '.')} {m.group(9)}"
            data.append({'date': current_date, 'hour': hour, 'rx': rx, 'tx': tx, 'total': total, 'avg': avg})
    logging.info(f"[parse_hourly] DATA: {data}")
    logging.info(f"[parse_hourly] PARSED {len(data)} rows: {data[:3]}")
    if not data:
        logging.warning("[parse_hourly] NO DATA PARSED!")
    return data[-24:]

def parse_hourly_full():
    out = get_vnstat_output(['-h'])
    lines = out.splitlines()
    data = []
    for line in lines:
        m = re.match(r"\s*(\d{4}-\d{2}-\d{2})\s+(\d{2}):00\s+([\d,\.]+)\s+(\w+)\s+([\d,\.]+)\s+(\w+)\s+([\d,\.]+)\s+(\w+)\s+([\d,\.]+)\s+(\w+)", line)
        if m:
            date = m.group(1)
            hour = m.group(2)
            rx = f"{m.group(3).replace(',', '.')} {m.group(4)}"
            tx = f"{m.group(5).replace(',', '.')} {m.group(6)}"
            total = f"{m.group(7).replace(',', '.')} {m.group(8)}"
            avg = f"{m.group(9).replace(',', '.')} {m.group(10)}"
            data.append({'date': date, 'hour': hour, 'rx': rx, 'tx': tx, 'total': total, 'avg': avg})
    return data

def parse_daily():
    out = get_vnstat_output(['-d'])
    logging.info(f"[parse_daily] RAW OUTPUT:\n{out}")
    lines = out.splitlines()
    data = []
    for line in lines:
        m = re.match(r"\s*(\d{4}-\d{2}-\d{2})\s+([\d,\.]+)\s+(\w+)\s*\|\s*([\d,\.]+)\s+(\w+)\s*\|\s*([\d,\.]+)\s+(\w+)\s*\|\s*([\d,\.]+)\s+(\w+)", line)
        if m:
            date = m.group(1)
            rx = f"{m.group(2).replace(',', '.')} {m.group(3)}"
            tx = f"{m.group(4).replace(',', '.')} {m.group(5)}"
            total = f"{m.group(6).replace(',', '.')} {m.group(7)}"
            avg = f"{m.group(8).replace(',', '.')} {m.group(9)}"
            data.append({'date': date, 'rx': rx, 'tx': tx, 'total': total, 'avg': avg})
    logging.info(f"[parse_daily] DATA: {data}")
    logging.info(f"[parse_daily] PARSED {len(data)} rows: {data[:3]}")
    if not data:
        logging.warning("[parse_daily] NO DATA PARSED!")
    return data

def parse_daily_full():
    out = get_vnstat_output(['-d'])
    lines = out.splitlines()
    data = []
    for line in lines:
        m = re.match(r"\s*(\d{4}-\d{2}-\d{2})\s+([\d,\.]+)\s+(\w+)\s+([\d,\.]+)\s+(\w+)\s+([\d,\.]+)\s+(\w+)\s+([\d,\.]+)\s+(\w+)", line)
        if m:
            date = m.group(1)
            rx = f"{m.group(2).replace(',', '.')} {m.group(3)}"
            tx = f"{m.group(4).replace(',', '.')} {m.group(5)}"
            total = f"{m.group(6).replace(',', '.')} {m.group(7)}"
            avg = f"{m.group(8).replace(',', '.')} {m.group(9)}"
            data.append({'date': date, 'rx': rx, 'tx': tx, 'total': total, 'avg': avg})
    return data

def parse_monthly():
    out = get_vnstat_output(['-m'])
    logging.info(f"[parse_monthly] RAW OUTPUT:\n{out}")
    lines = out.splitlines()
    data = []
    for line in lines:
        m = re.match(r"\s*(\d{4}-\d{2})\s+([\d,\.]+)\s+(\w+)\s*\|\s*([\d,\.]+)\s+(\w+)\s*\|\s*([\d,\.]+)\s+(\w+)\s*\|\s*([\d,\.]+)\s+(\w+)", line)
        if m:
            date = m.group(1)
            rx = f"{m.group(2).replace(',', '.')} {m.group(3)}"
            tx = f"{m.group(4).replace(',', '.')} {m.group(5)}"
            total = f"{m.group(6).replace(',', '.')} {m.group(7)}"
            avg = f"{m.group(8).replace(',', '.')} {m.group(9)}"
            data.append({'date': date, 'rx': rx, 'tx': tx, 'total': total, 'avg': avg})
    logging.info(f"[parse_monthly] DATA: {data}")
    logging.info(f"[parse_monthly] PARSED {len(data)} rows: {data[:3]}")
    if not data:
        logging.warning("[parse_monthly] NO DATA PARSED!")
    return data

def parse_monthly_full():
    out = get_vnstat_output(['-m'])
    lines = out.splitlines()
    data = []
    for line in lines:
        m = re.match(r"\s*(\d{4}-\d{2})\s+([\d,\.]+)\s+(\w+)\s+([\d,\.]+)\s+(\w+)\s+([\d,\.]+)\s+(\w+)\s+([\d,\.]+)\s+(\w+)", line)
        if m:
            month = m.group(1)
            rx = f"{m.group(2).replace(',', '.')} {m.group(3)}"
            tx = f"{m.group(4).replace(',', '.')} {m.group(5)}"
            total = f"{m.group(6).replace(',', '.')} {m.group(7)}"
            avg = f"{m.group(8).replace(',', '.')} {m.group(9)}"
            data.append({'month': month, 'rx': rx, 'tx': tx, 'total': total, 'avg': avg})
    return data 