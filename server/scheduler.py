from apscheduler.schedulers.background import BackgroundScheduler
from app import sendDailyMeme

scheduler = BackgroundScheduler()

@scheduler.scheduled_job('cron', second=9)
def daily_meme():
    sendDailyMeme()


if __name__ == "__main__":
    scheduler.start()