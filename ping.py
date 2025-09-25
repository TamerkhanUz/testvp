# ping.py
import asyncio
import subprocess
from playwright.async_api import async_playwright

async def open_chrome():
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)  # headless=False -> oynali rejim
            page = await browser.new_page()
            await page.goto("https://google.com")
            print("Chrome ishga tushdi. Iltimos 'ha' deb yozing.")
            
            javob = input(">>> ").strip().lower()
            if javob == "ha":
                while True:
                    subprocess.run(["ping", "google.com"])
                    await asyncio.sleep(120)  # 2 daqiqa kutish
            else:
                print("Bekor qilindi.")
    except Exception as e:
        print("Chrome ochilmadi. Chrome to'g'ri o'rnatilganligiga ishonch hosil qiling.")
        print("Xato:", e)

asyncio.run(open_chrome())
