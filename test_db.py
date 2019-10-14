import pickle

from push.push_util import Db, parse_course_hint

if __name__ == '__main__':

    with Db() as c:
        c.execute("SELECT bind_qq,course_table FROM user INNER JOIN course on user.uid = course.uid")

        res = c.fetchall()
        for id, course in res:
            a = parse_course_hint(pickle.loads(course),4)
            print(a)
