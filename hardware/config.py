"""Shared settings for the ANAAJ RAKSHAK bridge server (hardware/server.py)."""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
WEB_DIR = os.path.join(HERE, "..", "website")

HOST = "127.0.0.1"        # use "0.0.0.0" to open the site from a phone / other PC on the same Wi-Fi
PORT = 8000
OPEN_BROWSER = True

POLL_INTERVAL = 15        # seconds between ThingSpeak reads (only for source = "thingspeak")
STALE_AFTER = 120         # seconds without a new reading -> board shown OFFLINE
HISTORY_BACKFILL = 500    # past readings loaded when the server starts (thingspeak boards)
HISTORY_MAX = 5000        # readings kept in memory per board

# ---------- BOARDS ----------
#  source "serial"    : read a real ESP32 over USB (needs: pip install pyserial)
#  source "thingspeak": read it over the internet
#  source "simulated" : built-in simulated UNHEALTHY-wheat unit, no hardware and no COM port needed.
#                       "follow" makes it online exactly while the named board is online.
BOARDS = [
    {"key": "unit_1", "short": "Healthy", "label": "AnaajRakshak1 (healthy wheat)",
     "source": "serial", "port": "COM11", "baud": 115200,
     "channel_id": 3562028, "read_api_key": "P21E9GY7Y6A0A732"},        # key only used when source = "thingspeak"
    {"key": "unit_2", "short": "Unhealthy", "label": "AnaajRakshak2 (unhealthy wheat, simulated)",
     "source": "simulated", "follow": "unit_1",
     "clean_mv": {"mq135": 350, "mq3": 300, "mq7": 260},               # clean-air reference used for the ppm estimate
     "channel_id": 3562033, "read_api_key": ""},
]

# ---------- ALERT THRESHOLDS ----------
RISK_WARN = 50            # firmware risk score (0-100)
RISK_DANGER = 75
GRAIN_TEMP_WARN = 35.0    # deg C
HEAT_RATE_WARN = 2.0      # deg C per hour (grain probe trend)
RH_WARN = 85.0            # % RH
DEW_MARGIN = 2.0          # warn when grain is within this many deg C of the dew point
GAS_RATE_PPM_WARN = 100.0 # MQ135 gas level rise, ppm per hour
HIDE_SENSOR_FAULT_ALERTS = True   # True = no "Sensor fault" / "Grain probe missing" banners. False = show them.

# ---------- GAS SENSORS: demo fill-in + mV -> ppm estimate ----------
SIMULATE_SENSORS = ["mq135", "mq7"]   # sensors that report NO DATA get demo readings. [] = off
MQ_VCC = 5.0          # supply voltage of the MQ modules (V)
MQ_RL_KOHM = 10.0     # load resistor on the module (kOhm)
MQ_ADC_SCALE = 1.0    # 1.0 = AO wired straight to the ESP32; 1.5 = 10k/20k divider (AO = pin voltage x 1.5)
CAL_SAMPLES = 30      # clean-air readings (after warm-up) used to calibrate R0; saved in hardware/data/

# ppm range the demo (simulated) sensors move within. CO2-like safe range 400-1000 ppm, CO-like safe limit 9 ppm.
SIM_RANGE = {"mq135": (410, 470), "mq7": (0.6, 1.8)}

# ---------- GEMINI (Analysis page) ----------
GEMINI_API_KEY = "AQ.Ab8RN6LQSbC5Z-eaj28dYeH2YPSQGeA1Oa__3S4NhWD_t6KGFQ"                      # paste your key here (keep it private, never share this file)
GEMINI_MODEL = "gemini-3.5-flash-lite"   # if you get "model not found", try "gemini-flash-latest"