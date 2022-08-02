# egov_scraper
A dead simple script for scraping egov dot uscis dot gov


## How to use?

1. Create a virtual environment and install dependencies, e.g.:

```
$ virtualenv -p /usr/bin/python3.8 venv
$ . ./venv/bin/activate
(venv) $ pip install -r requirements.txt
```

1. Provide a list of receipts in a file `cases.txt` (single # per line)
2. Run: `python3 scraper.py`

Using example `cases.txt` you should get something like this:

```
(venv) $ python scraper.py
Receipt (WAC1101250960) has status 'Case Was Approved'
Receipt (WAC1315850523) has status 'Withdrawal Acknowledgement Notice Was Sent'
```
