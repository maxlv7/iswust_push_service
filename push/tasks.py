import pickle
from datetime import datetime

import pytz
import requests

from main_push import app, executor
from push.push_config import update_url, key, push_qqbot_url
from push.push_util import Db, send_private_msg, parse_course_hint


def get_(id):
    requests.get(update_url + str(int(id) ^ key))


def get_beijing_day():
    tz = pytz.timezone('Asia/Shanghai')  # 东八区

    return datetime.now(tz).timetuple().tm_wday + 1


def push_msg(qq, course_table):
    day = get_beijing_day()
    msg = parse_course_hint(course_table, day)
    verifycode = int(qq) ^ key
    res = requests.post(push_qqbot_url, json=send_private_msg(qq, msg, verifycode))
    if int(res.json()["code"]) == 200:
        print(f"success push to {qq}")


@app.task()
def update_all_course():
    # 查找出所有的用户
    with Db() as c:
        c.execute("SELECT bind_qq FROM user")
        l = []
        for x in c.fetchall():
            l.append(x[0])
    # 请求服务端(会自动更新)
    for id in l:
        executor.submit(get_(id))
        print(f"done id is {id}")


@app.task()
def send_course():
    # 查出所有学生和他们的课表
    with Db() as c:
        c.execute("SELECT bind_qq,course_table FROM user INNER JOIN course on user.uid = course.uid")
        res = c.fetchall()
        for id, course in res:
            executor.submit(push_msg(id, pickle.loads(course)))
