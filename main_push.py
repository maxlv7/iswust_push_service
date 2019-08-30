from concurrent.futures import ThreadPoolExecutor

from celery import Celery
from celery.schedules import crontab

from push.push_config import redis_url

executor = ThreadPoolExecutor(30)

app = Celery(
    __name__,
    broker=redis_url,
    backend=redis_url,
    include=['push.tasks']
)

app.conf.beat_schedule = {
    'update_course': {
        'task': 'push.tasks.update_all_course',
        'schedule': crontab(minute=0,hour=5,day_of_week='0'),
        'args': (),
    },
    'send_course': {
        'task': 'push.tasks.send_course',
        'schedule': crontab(minute='0,30',hour=7),
        'args': (),
    },
}
app.conf.update(
    enable_utc=True,
    timezone='Asia/Shanghai',
)

if __name__ == '__main__':
    app.worker_main()
    # 启动 celery
    # celery -A main_push worker -B

    # 启动flower
    #celery -A main_push flower --port=5555