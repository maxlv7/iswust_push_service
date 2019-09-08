import pickle
from datetime import datetime

import pytz
import requests

from main_push import app, executor
from push.push_config import update_url, key, push_qqbot_url
from push.push_util import Db, send_private_msg, parse_course_hint, bot_hash
from push.redis_util import r


def get_(qq):
    res = requests.get(update_url + str(bot_hash(qq))).json()
    msg = res["msg"]
    if int(res["code"]) == 200:
        r.sadd("update_success", f"update {qq} {msg}")
    else:
        r.sadd("update_fail", f"fail update {qq} {msg}")


def get_beijing_day():
    tz = pytz.timezone('Asia/Shanghai')  # 东八区

    return datetime.now(tz).timetuple().tm_wday + 1


def push_msg(qq, course_table):
    day = get_beijing_day()
    msg = parse_course_hint(course_table, day)
    verifycode = int(qq) ^ key
    res = requests.post(push_qqbot_url, json=send_private_msg(qq, msg, verifycode))
    if int(res.json()["code"]) == 200:
        r.sadd("push_status_success", f"success push to->{qq}")
    else:
        r.sadd("push_status_fail", f"fail push to->{qq}")


def retry_push_msg(qq, course_table):
    day = get_beijing_day()
    msg = parse_course_hint(course_table, day)
    verifycode = int(qq) ^ key
    res = requests.post(push_qqbot_url, json=send_private_msg(qq, msg, verifycode))
    if int(res.json()["code"]) == 200:
        r.sadd("push_status_success", f"success push to->{qq}")
        r.srem("push_status_fail", f"fail push to->{qq}")
    else:
        r.sadd("push_status_fail", f"fail push to->{qq}")


@app.task()
def update_all_course():
    # 查找出所有的用户
    with Db() as c:
        c.execute("SELECT bind_qq FROM user")
        l = []
        for x in c.fetchall():
            l.append(x[0])
    # 请求服务端(会自动更新)
    for qq in l:
        executor.submit(get_(qq))
    return "Update all course!"


@app.task()
def send_course():
    # 查出所有学生和他们的课表
    with Db() as c:
        c.execute("SELECT bind_qq,course_table FROM user INNER JOIN course on user.uid = course.uid")
        res = c.fetchall()
        for qq, course in res:
            executor.submit(push_msg(qq, pickle.loads(course)))
    return "Successfully execute all tasks"


@app.task()
def check_push_status():
    if r.scard("push_status_fail") == 0:
        return "All the pushes were successfully completed"
    else:
        # retry push
        all_fail = r.smembers("push_status_fail")
        for x in all_fail:
            qq = x[x.index(">") + 1:]
            with Db() as c:
                c.execute("select uid from user where bind_qq={}".format(qq))
                uid = c.fetchone()[0]
                c.execute("SELECT course_table FROM course where uid = {}".format(uid))
                course = c.fetchone()[0]
            executor.submit(retry_push_msg(qq, pickle.loads(course)))
        return "Retry one time success!"


@app.task()
def clear_today_key():
    msg = ""
    if r.expire("push_status_fail", -1):
        msg += "Clear key{push_status_fail} success!\n"
    if r.expire("push_status_success", -1):
        msg += "Clear key{push_status_success} success!\n"
    return msg
