import subprocess
import re
from datetime import datetime
import logging
from config import VNSTAT_IFACE, TOP_MIN5_COUNT, LOG_FILE, LOG_LEVEL, LOG_FORMAT

# logging.basicConfig(filename='vnstat_dashboard.log', level=logging.INFO, format='%(asctime)s %(message)s')

def validate_interface_name(interface):
    """Validate network interface name to prevent command injection"""
    if not interface:
        raise ValueError("Interface name cannot be empty")
    
    # Allow only alphanumeric characters, dots, hyphens, and underscores
    if not re.match(r'^[a-zA-Z0-9._-]+$', interface):
        raise ValueError(f"Invalid interface name: {interface}")
    
    # Prevent excessively long interface names
    if len(interface) > 15:  # Linux interface names are typically <= 15 chars
        raise ValueError(f"Interface name too long: {interface}")
    
    return interface

def get_vnstat_output(args):
    try:
        validated_interface = validate_interface_name(VNSTAT_IFACE)
        # Use list format to prevent shell injection
        cmd = ['vnstat', '-i', validated_interface] + args
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode != 0:
            logging.error(f"vnstat command failed with code {result.returncode}: {result.stderr}")
            return ""
            
        return result.stdout
    except (subprocess.TimeoutExpired, ValueError) as e:
        logging.error(f"Error executing vnstat command: {e}")
        return ""

def parse_5min():
    out = get_vnstat_output(['-5'])
    if not out:
        logging.warning("[parse_5min] No vnstat output received")
        return []
        
    logging.debug(f"[parse_5min] Processing {len(out.splitlines())} lines")
    lines = out.splitlines()
    data = []
    current_date = ""
    current_hour = ""
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Match date lines
        date_match = re.match(r"(\d{4}-\d{2}-\d{2})", line)
        if date_match:
            current_date = date_match.group(1)
            continue
            
        # Match hour lines  
        hour_match = re.match(r"(\d{1,2}):00", line)
        if hour_match:
            current_hour = hour_match.group(1).zfill(2)  # Ensure 2-digit format
            continue
            
        # Match data lines with more flexible regex
        m = re.match(
            r"(\d{1,2}:\d{2})\s+([\d,\.]+)\s*(\w+)\s*\|\s*([\d,\.]+)\s*(\w+)\s*\|\s*([\d,\.]+)\s*(\w+)\s*\|\s*([\d,\.]+)\s*(\w+)",
            line)
        if m and current_date and current_hour:
            try:
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
            except (IndexError, AttributeError) as e:
                logging.warning(f"[parse_5min] Failed to parse line: {line} - {e}")
                continue
                
    logging.info(f"[parse_5min] Successfully parsed {len(data)} entries")
    if not data:
        logging.warning("[parse_5min] NO DATA PARSED!")
    return data[-TOP_MIN5_COUNT:] if data else []

def parse_hourly():
    out = get_vnstat_output(['-h'])
    if not out:
        logging.warning("[parse_hourly] No vnstat output received")
        return []
        
    logging.debug(f"[parse_hourly] Processing {len(out.splitlines())} lines")
    lines = out.splitlines()
    data = []
    current_date = ""
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Match date lines
        m_date = re.match(r"(\d{4}-\d{2}-\d{2})", line)
        if m_date:
            current_date = m_date.group(1)
            continue
            
        # Match hourly data lines
        m = re.match(r"(\d{1,2}):00\s+([\d,\.]+)\s*(\w+)\s*\|\s*([\d,\.]+)\s*(\w+)\s*\|\s*([\d,\.]+)\s*(\w+)\s*\|\s*([\d,\.]+)\s*(\w+)", line)
        if m and current_date:
            try:
                hour = m.group(1).zfill(2)  # Ensure 2-digit format
                rx = f"{m.group(2).replace(',', '.')} {m.group(3)}"
                tx = f"{m.group(4).replace(',', '.')} {m.group(5)}"
                total = f"{m.group(6).replace(',', '.')} {m.group(7)}"
                avg = f"{m.group(8).replace(',', '.')} {m.group(9)}"
                data.append({'date': current_date, 'hour': hour, 'rx': rx, 'tx': tx, 'total': total, 'avg': avg})
            except (IndexError, AttributeError) as e:
                logging.warning(f"[parse_hourly] Failed to parse line: {line} - {e}")
                continue
                
    logging.info(f"[parse_hourly] Successfully parsed {len(data)} entries")
    if not data:
        logging.warning("[parse_hourly] NO DATA PARSED!")
    return data  # Return all data, let caller decide how many to use

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
    if not out:
        logging.warning("[parse_daily] No vnstat output received")
        return []
        
    logging.debug(f"[parse_daily] Processing {len(out.splitlines())} lines")
    lines = out.splitlines()
    data = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Match daily data lines
        m = re.match(r"(\d{4}-\d{2}-\d{2})\s+([\d,\.]+)\s*(\w+)\s*\|\s*([\d,\.]+)\s*(\w+)\s*\|\s*([\d,\.]+)\s*(\w+)\s*\|\s*([\d,\.]+)\s*(\w+)", line)
        if m:
            try:
                date = m.group(1)
                rx = f"{m.group(2).replace(',', '.')} {m.group(3)}"
                tx = f"{m.group(4).replace(',', '.')} {m.group(5)}"
                total = f"{m.group(6).replace(',', '.')} {m.group(7)}"
                avg = f"{m.group(8).replace(',', '.')} {m.group(9)}"
                data.append({'date': date, 'rx': rx, 'tx': tx, 'total': total, 'avg': avg})
            except (IndexError, AttributeError) as e:
                logging.warning(f"[parse_daily] Failed to parse line: {line} - {e}")
                continue
                
    logging.info(f"[parse_daily] Successfully parsed {len(data)} entries")
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
    if not out:
        logging.warning("[parse_monthly] No vnstat output received")
        return []
        
    logging.debug(f"[parse_monthly] Processing {len(out.splitlines())} lines")
    lines = out.splitlines()
    data = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Match monthly data lines
        m = re.match(r"(\d{4}-\d{2})\s+([\d,\.]+)\s*(\w+)\s*\|\s*([\d,\.]+)\s*(\w+)\s*\|\s*([\d,\.]+)\s*(\w+)\s*\|\s*([\d,\.]+)\s*(\w+)", line)
        if m:
            try:
                date = m.group(1)
                rx = f"{m.group(2).replace(',', '.')} {m.group(3)}"
                tx = f"{m.group(4).replace(',', '.')} {m.group(5)}"
                total = f"{m.group(6).replace(',', '.')} {m.group(7)}"
                avg = f"{m.group(8).replace(',', '.')} {m.group(9)}"
                data.append({'date': date, 'rx': rx, 'tx': tx, 'total': total, 'avg': avg})
            except (IndexError, AttributeError) as e:
                logging.warning(f"[parse_monthly] Failed to parse line: {line} - {e}")
                continue
                
    logging.info(f"[parse_monthly] Successfully parsed {len(data)} entries")
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