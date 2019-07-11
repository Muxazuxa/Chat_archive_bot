from celery import Celery
from celery.schedules import crontab
from datetime import date, timedelta
from config import *
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
import smtplib
import ssl
import os

app = Celery(broker='redis://redis:6379')
app.conf.timezone = 'Asia/Bishkek'


@app.task
def send_archives():

    yesterday = date.today() - timedelta(days=1)

    if len(os.listdir('archives')):
        msg = MIMEMultipart()
        msg['Subject'] = 'Archives for ' + yesterday.strftime('%d_%m_%Y')
        msg['From'] = EMAIL_HOST_USER
        msg['To'] = EMAIL_HOST_RECEIVER

        for filename in os.listdir('archives'):
            with open(os.path.join('archives', filename), 'rb') as attachment:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.read())
                encoders.encode_base64(part)
                part.add_header(
                    "Content-Disposition",
                    f"attachment; filename={filename}",
                )
                msg.attach(part)
            os.unlink(os.path.join('archives', filename))

        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(EMAIL_HOST, EMAIL_PORT, context=context) as server:
            server.login(EMAIL_HOST_USER, EMAIL_HOST_PASSWORD)
            server.sendmail(EMAIL_HOST_USER, EMAIL_HOST_RECEIVER, msg.as_string())


app.conf.beat_schedule={
    'send-mail': {
        'task': 'tasks.send_archives',
        'schedule': crontab(hour=0, minute=0),  # Send archives every midnight
    },
}