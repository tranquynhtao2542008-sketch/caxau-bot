bets])} cược\n💰 {game.total_bet:,} VND", parse_mode="Markdown")
        await asyncio.sleep(1)
    game.status = 'locked'
    await bot.send_message(chat_id, "🔒 ĐÃ KHÓA! Đang tung xúc xắc...", parse_mode="Markdown")
    await asyncio.sleep(0.5)
    dice1, dice2, dice3 = random.randint(1, 6), random.randint(1, 6), random.randint(1, 6)
    total = dice1 + dice2 + dice3
    is_tai = total >= 11
    is_chan = total % 2 == 0
    results, total_win = {}, 0
    for bet_type, bet_list in game.bets.items():
        if not bet_list: continue
        is_win = False
        if bet_type == 'tai' and is_tai: is_win = True
        elif bet_type == 'xiu' and not is_tai: is_win = True
        elif bet_type == 'chan' and is_chan: is_win = True
        elif bet_type == 'le' and not is_chan: is_win = True
        elif bet_type == 'tai_le' and is_tai and not is_chan: is_win = True
        elif bet_type == 'tai_chan' and is_tai and is_chan: is_win = True
        elif bet_type == 'xiu_le' and not is_tai and not is_chan: is_win = True
        elif bet_type == 'xiu_chan' and not is_tai and is_chan: is_win = True
        current_type = None
        for code, info in BET_TYPES.items():
            if info['type'] == bet_type: current_type = code; break
        if is_win:
            win_amount = int(sum([b['amount'] for b in bet_list]) * BET_TYPES[current_type]['rate'])
            total_win += win_amount
            for bet in bet_list:
                individual_win = int(bet['amount'] * BET_TYPES[current_type]['rate'])
                db.update_balance(bet['user_id'], individual_win, 'win', f"Thắng {current_type}")
                db.save_game_result(bet['user_id'], session_id, current_type, bet['amount'], individual_win, dice1, dice2, dice3, total, "THẮNG")
            results[current_type] = {'status': 'WIN', 'count': len(bet_list), 'amount': win_amount}
        else:
            for bet in bet_list: db.save_game_result(bet['user_id'], session_id, current_type, bet['amount'], 0, dice1, dice2, dice3, total, "THUA")
            results[current_type] = {'status': 'LOSE', 'count': len(bet_list), 'amount': 0}
    db.conn.commit()
    dice_emoji = {1: "⚀", 2: "⚁", 3: "⚂", 4: "⚃", 5: "⚄", 6: "⚅"}
    headers = ["CHỈ SỐ", "KẾT QUẢ"]
    rows = [["🎲 Xúc xắc", f"{dice_emoji[dice1]} {dice_emoji[dice2]} {dice_emoji[dice3]}"], ["🎯 Tổng", f"{total} điểm"], ["🟢 TÀI", "✅" if is_tai else "❌"], ["🔴 XỈU", "✅" if not is_tai else "❌"], ["⚪ CHẴN", "✅" if is_chan else "❌"], ["⚫ LẺ", "✅" if not is_chan else "❌"]]
    result_table = TableUI.create_table(headers, rows, f"🎲 KẾT QUẢ PHIÊN #{session_id}")
    detail_headers = ["CỬA", "SỐ NGƯỜI", "TIỀN"]
    detail_rows = []
    for bet_type, data in results.items():
        status = "🟢" if data['status'] == 'WIN' else "🔴"
        detail_rows.append([f"{status} {bet_type.upper()}", data['count'], f"{data['amount']:,}"])
    detail_table = TableUI.create_table(detail_headers, detail_rows, "📊 CHI TIẾT CÁC CỬA")
    summary_headers = ["CHỈ SỐ", "GIÁ TRỊ"]
    summary_rows = [["💰 Tổng cược", f"{game.total_bet:,} VND"], ["🏆 Tổng thưởng", f"{total_win:,} VND"], ["📈 Lợi nhuận", f"{total_win - game.total_bet:+,} VND"]]
    summary_table = TableUI.create_table(summary_headers, summary_rows, "📊 TỔNG KẾT")
    await bot.send_message(chat_id, f"{result_table}\n\n{detail_table}\n\n{summary_table}", parse_mode="Markdown")
    game.status = 'waiting'
    game.is_running = False
    await bot.send_message(chat_id, "🎰 **PHIÊN MỚI ĐÃ SẴN SÀNG!**\n📌 Đặt cược ngay: T 500K, X 500K, TL 500K...", parse_mode="Markdown")

async def main():
    print("🎰 BOT ROOM ĐÃ KHỞI ĐỘNG!")
    await dp.start_polling(bot)

if name == "__main__":
    asyncio.run(main())