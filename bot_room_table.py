import asyncio
import random
from datetime import datetime
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from config import ROOM_BOT_TOKEN, ADMIN_IDS, SESSION_DURATION, BET_TYPES
from database import db
from table_ui import TableUI

bot = Bot(token=ROOM_BOT_TOKEN)
dp = Dispatcher()

class GameState:
    def __init__(self):
        self.bets = {'tai': [], 'xiu': [], 'chan': [], 'le': [], 
                     'tai_le': [], 'tai_chan': [], 'xiu_le': [], 'xiu_chan': []}
        self.players = {}
        self.total_bet = 0
        self.status = 'waiting'
        self.countdown = SESSION_DURATION
        self.dice = []
        self.total = None
        self.session_id = 0
        self.is_running = False

game = GameState()

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    user_id = message.from_user.id
    user = db.get_user(user_id)
    if not user:
        db.create_user(user_id, message.from_user.username, message.from_user.full_name)
        user = db.get_user(user_id)
    
    headers = ["CỬA CƯỢC", "CÁCH ĐẶT", "TỶ LỆ"]
    rows = [
        ["🟢 TÀI", "T 500K", "x0.97"],
        ["🔴 XỈU", "X 500K", "x0.97"],
        ["⚪ CHẴN", "C 500K", "x0.97"],
        ["⚫ LẺ", "L 500K", "x0.97"],
        ["🎯 TÀI LẺ", "TL 500K", "x3.5"],
        ["🎯 TÀI CHẴN", "TC 500K", "x3.5"],
        ["🎯 XỈU LẺ", "XL 500K", "x3.5"],
        ["🎯 XỈU CHẴN", "XC 500K", "x3.5"]
    ]
    guide_table = TableUI.create_table(headers, rows, "📌 HƯỚNG DẪN ĐẶT CƯỢC")
    
    await message.answer(
        f"{guide_table}\n\n"
        f"💰 Số dư: {user[2]:,} VND\n"
        f"⭐ VIP: Level {user[10] if len(user) > 10 else 0}\n\n"
        f"💡 Mỗi phiên {SESSION_DURATION}s, 3 xúc xắc!",
        parse_mode="Markdown"
    )

@dp.message(F.text.regexp(r'^[TXC]\s+\d+[KMB]?$', ignore_case=True))
@dp.message(F.text.regexp(r'^(TL|TC|XL|XC)\s+\d+[KMB]?$', ignore_case=True))
async def handle_bet(message: types.Message):
    user_id = message.from_user.id
    text = message.text.upper()
    
    if game.status != 'waiting':
        await message.answer("⛔ Phiên đang xử lý! Chờ kết quả nhé!")
        return
    
    parts = text.split()
    bet_type_code = parts[0]
    amount_str = parts[1]
    
    if bet_type_code not in BET_TYPES:
        await message.answer("⚠️ Loại cược không hợp lệ!")
        return
    
    if amount_str.endswith('K'):
        amount = int(amount_str[:-1]) * 1000
    elif amount_str.endswith('M'):
        amount = int(amount_str[:-1]) * 1000000
    else:
        try:
            amount = int(amount_str)
        except:
            await message.answer("⚠️ Số tiền không hợp lệ!")
            return
    
    if amount < 1000:
        await message.answer("⚠️ Số tiền tối thiểu 1,000 VND!")
        return
    
    balance = db.get_balance(user_id)
    if balance < amount:
        await message.answer(f"❌ Số dư không đủ! Bạn có {balance:,} VND")
        return
    
    db.update_balance(user_id, -amount, 'bet', f"Cược {bet_type_code}")
    
    bet_info = {'user_id': user_id, 'amount': amount, 'time': datetime.now()}
    bet_key = BET_TYPES[bet_type_code]['type']
    game.bets[bet_key].append(bet_info)
    game.total_bet += amount
    game.players[user_id] = game.players.get(user_id, 0) + amount
    
    info = BET_TYPES[bet_type_code]
    confirm_table = TableUI.bet_confirmation_table(bet_type_code, amount, info['rate'], info['xiên'])
    await message.answer(confirm_table, parse_mode="Markdown")

@dp.message(Command("roll"))
async def cmd_roll(message: types.Message):
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("❌ Chỉ admin!")
        return
    
    if game.is_running:
        await message.answer("⚠️ Đã có phiên đang chạy!")
        return
    
    game.is_running = True
    asyncio.create_task(run_session(message.chat.id))

async def run_session(chat_id: int):
    game.session_id += 1
    session_id = game.session_id
    
    game.bets = {'tai': [], 'xiu': [], 'chan': [], 'le': [], 
                 'tai_le': [], 'tai_chan': [], 'xiu_le': [], 'xiu_chan': []}
    game.players = {}
    game.total_bet = 0
    
    await bot.send_message(
        chat_id,
        f"🎰 **PHIÊN #{session_id} ĐÃ MỞ!**\n"
        f"⏰ {SESSION_DURATION}s để đặt cược!",
        parse_mode="Markdown"
    )
    
    for i in range(SESSION_DURATION, 0, -1):
        if not game.is_running:
            return
        
        if i % 5 == 0 or i <= 10:
            await bot.send_message(
                chat_id,
                f"⏰ **CÒN {i}s**\n"
                f"📊 {sum([len(game.bets[t]) for t in game.bets])} cược\n"
                f"💰 {game.total_bet:,} VND",
                parse_mode="Markdown"
            )
        await asyncio.sleep(1)
    
    game.status = 'locked'
    await bot.send_message(chat_id, "🔒 **ĐÃ KHÓA!** Đang tung xúc xắc...", parse_mode="Markdown")
    await asyncio.sleep(0.5)
    
    dice1 = random.randint(1, 6)
    dice2 = random.randint(1, 6)
    dice3 = random.randint(1, 6)
    total = dice1 + dice2 + dice3
    
    is_tai = total >= 11
    is_chan = total % 2 == 0
    
    results = {}
    total_win = 0
    
    for bet_type, bet_list in game.bets.items():
        if not bet_list:
            continue
        
        is_win = False
        if bet_type == 'tai' and is_tai:
            is_win = True
        elif bet_type == 'xiu' and not is_tai:
            is_win = True
        elif bet_type == 'chan' and is_chan:
            is_win = True
        elif bet_type == 'le' and not is_chan:
            is_win = True
        elif bet_type == 'tai_le' and is_tai and not is_chan:
            is_win = True
        elif bet_type == 'tai_chan' and is_tai and is_chan:
            is_win = True
        elif bet_type == 'xiu_le' and not is_tai and not is_chan:
            is_win = True
        elif bet_type == 'xiu_chan' and not is_tai and is_chan:
            is_win = True
        
        current_type = None
        for code, info in BET_TYPES.items():
            if info['type'] == bet_type:
                current_type = code
                break
        
        if is_win:
            win_amount = int(sum([b['amount'] for b in bet_list]) * BET_TYPES[current_type]['rate'])
            total_win += win_amount
            
            for bet in bet_list:
                individual_win = int(bet['amount'] * BET_TYPES[current_type]['rate'])
                db.update_balance(bet['user_id'], individual_win, 'win', f"Thắng {current_type}")
                db.save_game_result(bet['user_id'], session_id, current_type, 
                                    bet['amount'], individual_win, dice1, dice2, dice3, total, "THẮNG")
            
            results[current_type] = {'status': 'WIN', 'count': len(bet_list), 'amount': win_amount}
        else:
            for bet in bet_list:
                db.save_game_result(bet['user_id'], session_id, current_type, 
                                    bet['amount'], 0, dice1, dice2, dice3, total, "THUA")
            
            results[current_type] = {'status': 'LOSE', 'count': len(bet_list), 'amount': 0}
    
    db.conn.commit()
    
    dice_emoji = {1: "⚀", 2: "⚁", 3: "⚂", 4: "⚃", 5: "⚄", 6: "⚅"}
    
    headers = ["CHỈ SỐ", "KẾT QUẢ"]
    rows = [
        ["🎲 Xúc xắc", f"{dice_emoji[dice1]} {dice_emoji[dice2]} {dice_emoji[dice3]}"],
        ["🎯 Tổng", f"{total} điểm"],
        ["🟢 TÀI", "✅" if is_tai else "❌"],
        ["🔴 XỈU", "✅" if not is_tai else "❌"],
        ["⚪ CHẴN", "✅" if is_chan else "❌"],
        ["⚫ LẺ", "✅" if not is_chan else "❌"]
    ]
    result_table = TableUI.create_table(headers, rows, f"🎲 KẾT QUẢ PHIÊN #{session_id}")
    
    detail_headers = ["CỬA", "SỐ NGƯỜI", "TIỀN"]
    detail_rows = []
    for bet_type, data in results.items():
        status = "🟢" if data['status'] == 'WIN' else "🔴"
        detail_rows.append([f"{status} {bet_type.upper()}", data['count'], f"{data['amount']:,}"])
    detail_table = TableUI.create_table(detail_headers, detail_rows, "📊 CHI TIẾT CÁC CỬA")
    
    summary_headers = ["CHỈ SỐ", "GIÁ TRỊ"]
    summary_rows = [
        ["💰 Tổng cược", f"{game.total_bet:,} VND"],
        ["🏆 Tổng thưởng", f"{total_win:,} VND"],
        ["📈 Lợi nhuận", f"{total_win - game.total_bet:+,} VND"]
    ]
    summary_table = TableUI.create_table(summary_headers, summary_rows, "📊 TỔNG KẾT")
    
    await bot.send_message(
        chat_id,
        f"{result_table}\n\n{detail_table}\n\n{summary_table}",
        parse_mode="Markdown"
    )
    
    game.status = 'waiting'
    game.is_running = False
    
    await bot.send_message(
        chat_id,
        "🎰 **PHIÊN MỚI ĐÃ SẴN SÀNG!**\n"
        "📌 Đặt cược ngay: T 500K, X 500K, TL 500K...",
        parse_mode="Markdown"
    )

async def main():
    print("🎰 BOT ROOM ĐÃ KHỞI ĐỘNG!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
