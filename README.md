### 启动celery

`celery -A main_push worker -B`

### 启动flower

`celery -A main_push flower --port=5555`