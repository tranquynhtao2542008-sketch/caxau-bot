#!/usr/bin/env python3
import asyncio
import logging
import os

os.makedirs("backups", exist_ok=True)
os.makedirs("images", exist_ok=True)
os.makedirs("logs", exist_ok=True)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def run_bot(bot_instance, name):
    try:
        logger.info(f"🚀 Khởi động {name}...")
        await bot_instance.start_polling()
    except Exception as e:
        logger.error(f"❌ Lỗi {name}: {e}")
        raise

async def main():
    print("""
╔═══════════════════════════════════════════════════════════════════╗
║                                                                   ║
║   🎰   C Á X Ấ U   -   R E P L I T   E D I T I O N             ║
║                                                                   ║
║   🤖 Bot Profile: @CaXauProfileBot                               ║
║   🎰 Bot Room: @CaXauRoomBot                                     ║
║   👑 Bot Admin: @CaXauAdminBot                                   ║
║   👤 Admin ID: 8823176709                                        ║
║                                                                   ║
╚═══════════════════════════════════════════════════════════════════╝
    """)
    logger.info("🚀 Đang khởi động 3 bot...")
    try:
        from bot_profile_table import dp as profile_dp
        from bot_room_table import dp as room_dp
        from bot_admin_table import dp as admin_dp
        logger.info("✅ Đã import 3 bot!")
        tasks = [
            asyncio.create_task(run_bot(profile_dp, "Bot Profile")),
            asyncio.create_task(run_bot(room_dp, "Bot Room")),
            asyncio.create_task(run_bot(admin_dp, "Bot Admin"))
        ]
        await asyncio.gather(*tasks)
    except KeyboardInterrupt: logger.info("🛑 Đã dừng!")
    except Exception as e: logger.error(f"❌ Lỗi: {e}"); raise

if name == "__main__":
    asyncio.run(main())