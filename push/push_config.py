qq_bot_base_url = "http://qq.artin.li:8080/api/push"
backend_base_url = "http://127.0.0.1:5000/"

key = 123456789

update_url = backend_base_url + "api/v1/course/getCourse?update=True&token={}&qq={}"
push_qqbot_url = qq_bot_base_url
get_week_url = backend_base_url + "api/v1/util/getWeek"
redis_url = "redis://127.0.0.1:6379/0"

db_ip = "127.0.0.1"
db_username = "iswust_backend"
db_password = "root"
db_name = "iswust_backend"
