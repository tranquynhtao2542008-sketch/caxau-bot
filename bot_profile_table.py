answer(f"{table}\n\n⏳ Admin sẽ xử lý trong 5 phút!", parse_mode="Markdown")

@dp.message(Command("bank"))
async def cmd_bank(message: types.Message):
    args = message.text.split()
    if len(args) < 2: await message.answer("⚠️ /bank [số_tài_khoản]"); return
    user_id = message.from_user.id
    db.cursor.execute("UPDATE users SET bank_account = ? WHERE user_id = ?", (args[1], user_id))
    db.conn.commit()
    await message.answer(f"✅ Đã cài STK: {args[1]}")

@dp.callback_query(F.data.startswith("profile_"))
async def profile_callbacks(callback: types.CallbackQuery):
    action = callback.data.split("_")[1]
    user_id = callback.from_user.id
    user = db.get_user(user_id)
    stats = db.get_user_stats(user_id)
    if action == 'balance':
        headers = ["CHỈ SỐ", "GIÁ TRỊ"]
        rows = [["💰 Số dư", f"{user[2]:,} VND"], ["💳 Tổng nạp", f"{user[3]:,} VND"], ["💸 Tổng rút", f"{user[4]:,} VND"]]
        table = TableUI.create_table(headers, rows, "💰 THÔNG TIN SỐ DƯ")
        await callback.message.edit_text(table, parse_mode="Markdown")
    elif action == 'stats':
        profit = stats['total_win'] - stats['total_bet']
        headers = ["CHỈ SỐ", "GIÁ TRỊ"]
        rows = [["🎮 Số ván", stats['games']], ["💰 Tổng cược", f"{stats['total_bet']:,} VND"], ["🏆 Tổng thắng", f"{stats['total_win']:,} VND"], ["📈 Tỷ lệ thắng", f"{stats['win_rate']}%"], ["📊 Lợi nhuận", f"{profit:+,} VND"]]
        table = TableUI.create_table(headers, rows, "📊 THỐNG KÊ CÁ NHÂN")
        await callback.message.edit_text(table, parse_mode="Markdown")
    elif action == 'vip':
        vip_level = user[10] if len(user) > 10 else 0
        vip_names = ['Tân Thủ', 'Đồng', 'Bạc', 'Vàng', 'Kim Cương', 'Huyền Thoại']
        vip_name = vip_names[vip_level] if vip_level <= 5 else 'Huyền Thoại'
        headers = ["THÔNG TIN", "GIÁ TRỊ"]
        rows = [["⭐ Cấp độ", f"VIP {vip_level}"], ["🏷️ Tên", vip_name], ["💰 Tổng nạp", f"{user[3]:,} VND"], ["🎁 Thưởng", f"+{vip_level * 2}%"], ["📈 Hạn mức", f"x{vip_level + 1}"]]
        table = TableUI.create_table(headers, rows, f"⭐ THÔNG TIN VIP")
        await callback.message.edit_text(table, parse_mode="Markdown")
    elif action == 'deposit': await cmd_nap(callback.message)
    elif action == 'withdraw': await cmd_rut(callback.message)
    elif action == 'bank':
        await callback.message.edit_text("🏦 **CÀI ĐẶT STK**\n\nGõ lệnh: /bank [số_tài_khoản]\nVD: /bank 123456789\n\n⚠️ STK phải chính chủ để rút tiền!", parse_mode="Markdown")
    elif action == 'history':
        history = db.cursor.execute('''SELECT type, amount, description, created_at FROM transactions WHERE user_id = ? ORDER BY created_at DESC LIMIT 10''', (user_id,)).fetchall()
        if not history: await callback.message.edit_text("📭 Chưa có lịch sử!"); return
        headers = ["LOẠI", "SỐ TIỀN", "THỜI GIAN"]
        rows = []
        for h in history:
            emoji = {'deposit': '⬆️', 'withdraw': '⬇️', 'bet': '🎲', 'win': '🏆'}.get(h[0], '📌')
            rows.append([f"{emoji} {h[0]}", f"{h[1]:,} VND", h[3].strftime("%H:%M %d/%m")])
        table = TableUI.create_table(headers, rows, "📋 LỊCH SỬ GIAO DỊCH")
        await callback.message.edit_text(table, parse_mode="Markdown")
    await callback.answer()

async def main():
    print("🤖 BOT PROFILE ĐÃ KHỞI ĐỘNG!")
    await dp.start_polling(bot)

if name == "__main__":
    asyncio.run(main())