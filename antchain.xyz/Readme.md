发送验证邮件、异步获取交易所数据使用了Celery任务队列,中间层使用了RabbitMQ



安装:
* `git clone https://github.com/lcux/antchain.xyz.git`
*   建立virtualenv隔离环境,比如`virtualenv venv && source venv/bin/activate`
*   安装依赖 `pip install -r requirement.txt`
*   确保RabbitMQ/MongoDB已安装并正常启动
*   开启celery任务队列`celery worker -A worker_celery.celery --loglevel=info`