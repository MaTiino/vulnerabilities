
from apscheduler.schedulers.background import BackgroundScheduler
from cisco_api import fetch_and_store_advisories

def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(fetch_and_store_advisories, 'interval', hours=12)
    scheduler.start()
