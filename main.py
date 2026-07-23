import os
import re
import time
import smtplib
from email.mime.text import MIMEText
import asyncio
from dotenv import load_dotenv
from playwright.async_api import async_playwright, expect
from bs4 import BeautifulSoup 

load_dotenv()
CLASS_SEARCH = "https://mycolleges.shr.nevada.edu/psp/spcssprd/TMC/HRMS/c/COMMUNITY_ACCESS.CLASS_SEARCH.GBL?FolderPath=PORTAL_ROOT_OBJECT.CO_EMPLOYEE_SELF_SERVICE.HC_CLASS_SEARCH_GBL&amp;IsFolder=false&amp;IgnoreParamTempl=FolderPath,IsFolder"

async def gather_html():
    """
        Desc:
            Gathers the html from the class search page and parses it for class availability.
        Args:
            None
        Return:
            None
    """
    async with async_playwright() as p:
        browser =  await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(CLASS_SEARCH, wait_until="networkidle")

        iframe = page.frame_locator("#ptifrmtgtframe")

        class_num_box_selector = 'input[id="SSR_CLSRCH_WRK_CLASS_NBR$10"]'
        class_num_box = iframe.locator(class_num_box_selector)
        await class_num_box.fill("50316")

        search_btn = iframe.locator('input[id="CLASS_SRCH_WRK2_SSR_PB_CLASS_SRCH"]')
        await search_btn.click()

        await page.wait_for_load_state("networkidle")
        await asyncio.sleep(3)

        class_num_link = iframe.locator('a[id="MTG_CLASS_NBR$0"]')
        await class_num_link.wait_for(state="attached")
        await class_num_link.click()

        await page.wait_for_load_state("networkidle")
        await asyncio.sleep(5)

        iframe_raw_html = await iframe.locator("html").inner_html()

        await browser.close()

        parse_class_avail(iframe_raw_html)

def parse_class_avail(html_content):
    """
        Desc:
            Parses the html content for class availability.
        Args:
            html_content: The html content to parse.
        Return:
            None
    """
    soup = BeautifulSoup(html_content, "html.parser")

    status_el = soup.find("span", id="SSR_CLS_DTL_WRK_SSR_DESCRSHORT")
    seats_el = soup.find("span", id="SSR_CLS_DTL_WRK_AVAILABLE_SEATS")

    status = status_el.get_text(strip=True) if status_el else "Not Found"
    seats = seats_el.get_text(strip=True) if seats_el else "Not Found"

    print("---- Results ----")
    print(f"Class Status: {status}")
    print(f"Available Seats: {seats}")

    if status == "Closed" or (int(seats) <= 0):
        print("ALERT: Class is closed and or full!")

    elif status == "Open" and (int(seats) > 0):
        print("ALERT: Class is available!")

        for i in range(1, 6):
            print(f"Sending alerts...")
            send_message_alert(status, seats, i)
            time.sleep(30)


def send_message_alert(status, seats, blast_num):
    """
        Desc:
            Sends an email alert to the user.
        Args:
            status: The status of the class.
            seats: The number of available seats.
        Return:
            None
    """
    sender_email = os.getenv("SENDER_EMAIL")
    sender_password = os.getenv("APP_PASSWORD")
    receiver_phone = os.getenv("RECIEVER_PHONE")

    body = f"[{blast_num}/5] WAKE UP YOUR CLASS IS OPEN! \n\nClass Status: {status}\nAvailable Seats: {seats}"
    msg = MIMEText(body)
    msg['From'] = sender_email
    msg['To'] = receiver_phone
    msg['Subject'] = "CLASS OPEN ALERT!"

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, receiver_phone, msg.as_string())
            print("Alert sent successfully!")
    except Exception as e:
        print(f"Failed to send alert: {e}")

if __name__ == "__main__":
    while True:
        try:
            asyncio.run(gather_html())
        except Exception as e:
            print(f"An error occurred: {e}")

        time.sleep(300)




