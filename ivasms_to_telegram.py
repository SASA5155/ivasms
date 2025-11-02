import asyncio
import aiohttp
from aiogram import Bot, Dispatcher
from bs4 import BeautifulSoup
import os

# الإعدادات (من متغيرات البيئة في Railway)
IVASMS_EMAIL = os.getenv("IVASMS_EMAIL")
IVASMS_PASSWORD = os.getenv("IVASMS_PASSWORD")
BOT_TOKEN = os.getenv("BOT_TOKEN")
GROUP_ID = int(os.getenv("GROUP_ID", "-1002783113539"))
CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", "10"))

LOGIN_URL = "https://www.ivasms.com/portal/login"
MY_SMS_URL = "https://www.ivasms.com/portal/live/my_sms"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


async def login_and_get_cookies(session: aiohttp.ClientSession):
    """تسجيل الدخول في IVASMS"""
    data = {
        "email": IVASMS_EMAIL,
        "password": IVASMS_PASSWORD,
    }
    async with session.post(LOGIN_URL, data=data) as resp:
        if resp.status == 200:
            print("[✅] تم تسجيل الدخول بنجاح.")
            return session.cookie_jar
        else:
            print("[❌] فشل تسجيل الدخول!")
            return None


async def fetch_messages(session: aiohttp.ClientSession):
    """قراءة الرسائل من صفحة my_sms"""
    async with session.get(MY_SMS_URL) as resp:
        html = await resp.text()
        soup = BeautifulSoup(html, "lxml")
        messages = []

        rows = soup.find_all("tr")
        for row in rows:
            cols = row.find_all("td")
            if len(cols) >= 2:
                sender = cols[0].text.strip()
                msg = cols[1].text.strip()
                messages.append((sender, msg))

        return messages


async def forward_new_messages():
    """متابعة الرسائل الجديدة"""
    print("🚀 البوت شغال وبيفحص الرسائل كل", CHECK_INTERVAL, "ثانية")

    last_messages = set()

    async with aiohttp.ClientSession() as session:
        await login_and_get_cookies(session)

        while True:
            try:
                messages = await fetch_messages(session)

                for sender, msg in messages:
                    if msg not in last_messages:
                        text = f"📩 **رسالة جديدة:**\n👤 المرسل: {sender}\n💬 المحتوى:\n`{msg}`"
                        await bot.send_message(GROUP_ID, text, parse_mode="Markdown")
                        print("[📨] رسالة جديدة أُرسلت للجروب:", msg)
                        last_messages.add(msg)

                await asyncio.sleep(CHECK_INTERVAL)

            except Exception as e:
                print("[⚠️] خطأ:", e)
                await asyncio.sleep(5)


async def main():
    await forward_new_messages()

if __name__ == "__main__":
    asyncio.run(main())
