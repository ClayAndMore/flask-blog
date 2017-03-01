import smtplib
import datetime
from email.mime.text import MIMEText

from flask_mail import Message

from MyBlog.extensions import flask_celery,mail
from MyBlog.models import Reminder

@flask_celery.task(
    bind=True,
    igonre_result=True,
    default_retry_delay=300,
    max_retries=5
)
def remind(self,primary_key):
    reminder=Reminder.query.get(primary_key)
    msg=MIMEText(reminder.text)
    msg['Subject'] = 'Welcome!'
    msg['FROM'] = '422516721@qq.com'
    msg['To'] = reminder.email

    try:
        smtp_server = smtplib.SMTP('localhost')
        smtp_server.starttls()
        smtp_server.login( '422516721@qq.com','fd135145..++')
        smtp_server.sendmail( msg['From'],
        [reminder.email],
        msg.as_string())
        smtp_server.close()
        return

    except Exception as err:
        self.retry(exc=err)


def on_reminder_save(mapper, connect, self):
    """Callbask for task remind."""
    remind.apply_async(args=(self.id), eta=self.date)