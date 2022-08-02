"""Dead simple script for scraping egov uscis gov."""

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
    "sec-ch-ua": (
        '".Not/A)Brand";v="99", "Google Chrome";v="103", "Chromium";v="103"'
    ),
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Linux"',
    "sec-gpc": "1",
}

data = {
    "changeLocale": "",
    "initCaseSearch": "CHECK STATUS",
}

uscis_url = "https://egov.uscis.gov/casestatus/mycasestatus.do"

with open("cases.txt", "r") as fp:
    case_numbers = [line.strip() for line in fp.readlines()]

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
            print(f"Receipt ({case}) has status '{status}'")
        except Exception as exc:
            print(f"Parsing status node for {case} went wrong. Blame me.")
            print(f"  Raised {exc}")
