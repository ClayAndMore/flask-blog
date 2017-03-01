import os
from celery import Celery
from MyBlog import create_app

def make_celery(app):
    celery=Celery(
        app.import_name,
        backend=app.config['CELERY_RESULT_BACKEND'],
        broker=app.config['CELERY_BROKER_URL']
    )

    celery.conf.update(app.config)
    TaskBase=celery.Task

    class ContextTask(TaskBase):
        abstract=True
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self,*args,**kwargs)

    celery.Task=ContextTask
    return celery

env = os.environ.get('BLOG_ENV', 'dev')
flask_app = create_app('MyBlog.config.%sConfig' % env.capitalize())
# 1. Each celery process needs to create an instance of the Flask application.
# 2. Register the celery object into the app object.
celery = make_celery(flask_app)