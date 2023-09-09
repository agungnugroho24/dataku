from apscheduler.schedulers.blocking import BlockingScheduler
import requests
import bappenas

sched = BlockingScheduler()

@sched.scheduled_job('cron', day_of_week='mon-sun', hour=5)
def refresh_cache():
    subjects = bappenas.get_subjects()
    for subject in subjects:
        base_url = "http://datakuapi.apps.pulselabjakarta.id/subject/{}".format(str(subject['id']))
        requests.get(base_url)
    print('Cache refreshed')
    return "Cache refreshed"
result = refresh_cache()
sched.start()