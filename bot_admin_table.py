upper(), f"{tx[3]:,}", "✅" if tx[4] == 'completed' else "⏳"])
    table = TableUI.create_table(headers, rows, "💰 DANH SÁCH GIAO DỊCH")
    await callback.message.edit_text(table, parse_mode="Markdown")
    await callback.answer()

@dp.callback_query(F.data == "admin_codes")
async def admin_codes(callback: types.CallbackQuery):
    if not is_admin(callback.from_user.id): await callback.answer("❌ Không có quyền!"); return
    codes = db.cursor.execute('''SELECT code, amount, used_count, usage_limit FROM gift_codes ORDER BY created_at DESC LIMIT 20''').fetchall()
    headers = ["CODE", "GIÁ TRỊ", "ĐÃ DÙNG", "GIỚI HẠN"]
    rows = []
    for c in codes: rows.append([f"`{c[0]}`", f"{c[1]:,}", c[2], c[3]])
    table = TableUI.create_table(headers, rows, "🎁 DANH SÁCH GIFTCODE")
    await callback.message.edit_text(table, parse_mode="Markdown")
    await callback.answer()

@dp.callback_query(F.data == "admin_backup")
async def admin_backup(callback: types.CallbackQuery):
    if not is_admin(callback.from_user.id): await callback.answer("❌ Không có quyền!"); return
    import shutil, os
    os.makedirs("backups", exist_ok=True)
    backup_file = f"backups/backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
    try:
        shutil.copy2("caxau.db", backup_file)
        headers = ["THÔNG TIN", "CHI TIẾT"]
        rows = [["✅ Trạng thái", "Thành công"], ["📁 File", backup_file], ["💾 Size", f"{os.path.getsize(backup_file):,} bytes"], ["📅 Thời gian", datetime.now().strftime("%d/%m/%Y %H:%M:%S")]]
        table = TableUI.create_table(headers, rows, "💾 BACKUP HỆ THỐNG")
        await callback.message.edit_text(table, parse_mode="Markdown")
    except Exception as e: await callback.message.edit_text(f"❌ Lỗi: {e}")
    await callback.answer()

@dp.message(Command("create_code"))
async def cmd_create_code(message: types.Message):
    if not is_admin(message.from_user.id): await message.answer("❌ Chỉ admin!"); return
    args = message.text.split()
    if len(args) < 2: await message.answer("⚠️ /create_code [số_tiền]"); return
    amount = int(args[1])
    import string, secrets
    code = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(8))
    db.create_gift_code(code, amount, message.from_user.id)
    await message.answer(f"✅ **CODE TẠO THÀNH CÔNG!**\n\n📌 Mã: `{code}`\n💰 {amount:,} VND", parse_mode="Markdown")

async def main():
    print("👑 BOT ADMIN ĐÃ KHỞI ĐỘNG!")
    await dp.start_polling(bot)

if name == "__main__":
    asyncio.run(main())