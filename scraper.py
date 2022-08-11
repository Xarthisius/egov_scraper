"""Dead simple script for scraping egov uscis gov."""

import os
import re
import time
from datetime import date, datetime

import requests
from bs4 import BeautifulSoup

headers = {
    "Accept": (
        "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,"
        "image/webp,image/apng;q=0.8,application/signed-exchange;v=b3;q=0.9"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Cache-Control": "max-age=0",
    "Connection": "keep-alive",
    "DNT": "1",
    "Origin": "https://egov.uscis.gov",
    "Referer": "https://egov.uscis.gov/casestatus/landing.do",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36"
    ),
    "sec-ch-ua": ('".Not/A)Brand";v="99", "Google Chrome";v="103", "Chromium";v="103"'),
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Linux"',
    "sec-gpc": "1",
}

data = {
    "changeLocale": "",
    "initCaseSearch": "CHECK STATUS",
}

uscis_url = "https://egov.uscis.gov/casestatus/mycasestatus.do"
date_regex = re.compile(
    (
        r"(On|As of)\s((Jan(uary)?|Feb(ruary)?|Mar(ch)?|Apr(il)?|May|Jun(e)?|Jul(y)?|Aug(ust)"
        r"?|Sep(tember)?|Oct(ober)?|Nov(ember)?|Dec(ember)?)\s+\d{1,2},\s+\d{4})|((1["
        r"0-2]|0?[1-9])/(3[01]|[12][0-9]|0?[1-9])/(?:[0-9]{2})?[0-9]{2})"
    )
)
form_regex = re.compile(r"Form\s(I.[0-9]{3})", re.IGNORECASE)

with open("cases.txt", "r") as fp:
    case_numbers = [line.strip() for line in fp.readlines()]


def run():
    results = ["receiptNo,status,statusSince\n"]

    with requests.Session() as session:
        for case in case_numbers:
            data["appReceiptNum"] = case
            response = session.post(
                "https://egov.uscis.gov/casestatus/mycasestatus.do",
                cookies={},
                headers=headers,
                data=data,
            )
            if not response.ok:
                print(f"Something went wrong with case: {case}")
                continue
            bs = BeautifulSoup(response.text, "lxml")
            status_node = bs.find("div", {"class": "current-status-sec"})
            if not status_node:
                print(f"Unable to find status element in the response ({case})")
            try:
                status = status_node.text.split("\t")[1].strip()
            except Exception as exc:
                print(f"Parsing status node for {case} went wrong. Blame me.")
                print(f"  Raised {exc}")

            full_text = bs.find("div", attrs={"class": "appointment-sec"}).p.text
            if (status_date := date_regex.match(full_text)):
                lastDate = status_date.group()
                if lastDate.startswith("On"):
                    lastDate = lastDate[3:]
                else:
                    lastDate = lastDate[6:]
                lastDate = datetime.strptime(lastDate, "%B %d, %Y").strftime("%Y-%m-%d")
            else:
                lastDate = "None"

            form_type = None
            if (form := form_regex.findall(full_text)):
                form_type = form[0]

            results.append(f"{case},{status},{str(lastDate)}\n")
            print(f"Receipt ({case}) has status '{status}' since {lastDate} ({form_type}).")

    if not os.path.isdir("outputs"):
        os.mkdir("outputs")

    with open(f"outputs/madhavan-{str(date.today())}.csv", "w") as fp:
        for line in results:
            fp.write(line)
    print("Wrote file!")


while True:
    run()
    time.sleep(6 * 3600)  # sleep for 6h
