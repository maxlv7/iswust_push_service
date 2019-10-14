import hashlib
import os

import pymysql

from push.push_config import db_ip, db_name, db_password, db_username


def bot_hash(message: str) -> str:
    message = str(message)
    try:
        key = os.environ.get("ENCRYPT_KEY").encode()
    except:
        key = '123456789'.encode()
    inner = hashlib.md5()
    inner.update(message.encode())
    outer = hashlib.md5()
    outer.update(inner.hexdigest().encode() + key)
    return outer.hexdigest()


def send_private_msg(user_id, message, token):
    msg = {
        "qq": user_id,
        "msg": message,
        "token": token
    }
    return msg


def tip(strs):
    after = strs.split('-')
    start = int(after[0])
    last = int(after[1])
    if start == 1 and last == 2:
        return "上午第一讲"
    if start == 1 and last == 4:
        return "上午一到二讲"
    if start == 2 and last == 2:
        return "上午第二讲"
    if start == 3 and last == 2:
        return "下午第一讲"
    if start == 3 and last == 4:
        return "下午一到二讲"
    if start == 4 and last == 2:
        return "下午第二讲"
    if start == 5 and last == 2:
        return "晚上第一讲"
    if start == 6 and last == 2:
        return "晚上第二讲"
    if start == 5 and last == 4:
        return "晚上一到二讲"


'''
今天的课程如下:
密码学(老王)---上午第一讲---东1402
密码学(老王)---上午第一讲---东1402
'''


def parse_course_hint(course_table, day: int):
    msg = '今天的课程如下:\n'
    body = course_table["body"]
    result = body["result"]
    curr_week = body['week']
    today_course_list = []
    for x in result:
        # 当周
        if curr_week >= int(x["qsz"]) and curr_week <= int(x["zzz"]):
            for i in range(len(x["class_time"])):
                # class_time [1@2-2, 3@3-2]
                if int(x["class_time"][i][0]) == day:
                    # 过滤出今天的课表
                    _course = {
                        "class_name": x["class_name"],
                        "class_time": x["class_time"][i][2:],
                        "location": x["location"][i],
                        "teacher_name": x["teacher_name"],
                    }
                    today_course_list.append(_course)

    today_course_list.sort(key=lambda e: e['class_time'][0])
    if len(today_course_list) == 0:
        msg = msg + "今天没有课哦!"
    for course in today_course_list:
        t = '{}\n- {}({})\n- {}\n\n'.format(tip(course["class_time"]), course["class_name"],
                                            course["teacher_name"], course["location"])
        msg = msg + t
    return msg[:-2]


class Db():
    def __init__(self):
        self._cursor = None
        self._conn = pymysql.connect(db_ip, db_username, db_password, db_name)

    def __enter__(self):

        self._cursor = self._conn.cursor()
        return self._cursor

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            # 发生错误，rollback
            if exc_type is not None:
                self._conn.rollback()
            else:
                self._conn.commit()
            if exc_val is not None or exc_tb is not None:
                pass
        except Exception as e:
            pass
        finally:
            self._cursor.close()
            self._conn.close()
            return True
