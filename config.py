import os
from dotenv import load_dotenv

load_dotenv()

PROFILE_BOT_TOKEN = os.getenv("PROFILE_BOT_TOKEN")
ROOM_BOT_TOKEN = os.getenv("ROOM_BOT_TOKEN")
ADMIN_BOT_TOKEN = os.getenv("ADMIN_BOT_TOKEN")

ADMIN_IDS = [int(x) for x in os.getenv("ADMIN_IDS", "8823176709").split(",")]

SESSION_DURATION = int(os.getenv("SESSION_DURATION", 45))
MIN_BET = int(os.getenv("MIN_BET", 1000))
MAX_BET = int(os.getenv("MAX_BET", 10000000))

RATES = {
    'tai': 0.97, 'xiu': 0.97, 'chan': 0.97, 'le': 0.97,
    'tai_le': 3.5, 'tai_chan': 3.5, 'xiu_le': 3.5, 'xiu_chan': 3.5
}

BET_TYPES = {
    'T': {'type': 'tai', 'name': 'TÀI', 'rate': 0.97, 'xiên': False},
    'X': {'type': 'xiu', 'name': 'XỈU', 'rate': 0.97, 'xiên': False},
    'C': {'type': 'chan', 'name': 'CHẴN', 'rate': 0.97, 'xiên': False},
    'L': {'type': 'le', 'name': 'LẺ', 'rate': 0.97, 'xiên': False},
    'TL': {'type': 'tai_le', 'name': 'TÀI LẺ', 'rate': 3.5, 'xiên': True},
    'TC': {'type': 'tai_chan', 'name': 'TÀI CHẴN', 'rate': 3.5, 'xiên': True},
    'XL': {'type': 'xiu_le', 'name': 'XỈU LẺ', 'rate': 3.5, 'xiên': True},
    'XC': {'type': 'xiu_chan', 'name': 'XỈU CHẴN', 'rate': 3.5, 'xiên': True}
}