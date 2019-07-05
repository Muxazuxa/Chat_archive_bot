from telegram.error import NetworkError, Unauthorized

from datetime import date
from config import *
from time import sleep
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
import smtplib, ssl
import os, telegram
import schedule

update_id = None


def main():
    global update_id
    bot = telegram.Bot(TOKEN)

    try:
        update_id = bot.get_updates()[0].update_id
    except IndexError:
        update_id = None

    schedule.every().day.at('00:00').do(send_archives)

    while True:
        try:
            echo(bot)
            schedule.run_pending()
        except NetworkError:
            sleep(1)
        except Unauthorized:
            update_id += 1


def send_archives():
    msg = MIMEMultipart()
    msg['Subject'] = 'Archives for ' + date.today().strftime('%d_%m_%Y')
    msg['From'] = EMAIL_HOST_USER
    msg['To'] = EMAIL_HOST_RECEIVER

    if len(os.listdir('archives')):
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


def echo(bot):

    global update_id

    for update in bot.get_updates(offset=update_id, timeout=10):
        update_id = update.update_id + 1

        if update.message:
            today = date.today().strftime("%d_%m_%Y_")
            group_name = str(update.message.chat.title).replace(" ", "_")
            message = str(update.message.text)
            user = update.message.from_user.first_name
            f = open(os.path.join('archives', today + group_name + '.txt'), "a+")
            f.write(user + ': ' + message + '\n')
            f.close()


if __name__ == '__main__':
    main()