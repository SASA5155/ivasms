import asyncio
import os
from aiogram import Bot
from playwright.async_api import async_playwright

# ---------------- إعدادات ----------------
IVASMS_EMAIL = os.getenv("IVASMS_EMAIL")
IVASMS_PASSWORD = os.getenv("IVASMS_PASSWORD")
BOT_TOKEN = os.getenv("BOT_TOKEN")
GROUP_ID = int(os.getenv("GROUP_ID"))
CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", "10"))

bot = Bot(token=BOT_TOKEN)

async def fetch_messages(page):
    await page.goto("https://www.ivasms.com/portal/live/my_sms")
    await page.wait_for_timeout(3000)  # انتظر 3 ثواني لتكملة تحميل JS

    rows = await page.query_selector_all("tr")
    messages = []

    for row in rows:
        cols = await row.query_selector_all("td")
        if len(cols) >= 2:
            sender = (await cols[0].inner_text()).strip()
            msg = (await cols[1].inner_text()).strip()
            messages.append((sender, msg))

    return messages

async def main():
    last_messages = set()
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto("https://www.ivasms.com/portal/login")

        # تسجيل الدخول
        await page.fill("input[name='email']", IVASMS_EMAIL)
        await page.fill("input[name='password']", IVASMS_PASSWORD)
        await page.click("button[type='submit']")
        await page.wait_for_timeout(5000)

        print("[✅] تم تسجيل الدخول بنجاح إلى IVASMS")

        while True:
            try:
                messages = await fetch_messages(page)
                for sender, msg in messages:
                    if msg not in last_messages:
                        text = f"📩 رسالة جديدة\n👤 المرسل: {sender}\n💬 المحتوى:\n`{msg}`"
                        await bot.send_message(GROUP_ID, text, parse_mode="Markdown")
                        print("[📨] رسالة جديدة أُرسلت:", msg)
                        last_messages.add(msg)
                await asyncio.sleep(CHECK_INTERVAL)
            except Exception as e:
                print("[⚠️] خطأ:", e)
                await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(main())
