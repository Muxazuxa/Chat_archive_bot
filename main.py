from telegram.error import NetworkError, Unauthorized

from datetime import date
from config import TOKEN
from time import sleep
import os
import telegram

update_id = None


def main():
    global update_id
    bot = telegram.Bot(TOKEN)

    try:
        update_id = bot.get_updates()[0].update_id
    except IndexError:
        update_id = None

    while True:
        try:
            echo(bot)
        except NetworkError:
            sleep(1)
        # The user has removed or blocked the bot.
        except Unauthorized:
            update_id += 1


def echo(bot):

    global update_id

    for update in bot.get_updates(offset=update_id, timeout=10):
        update_id = update.update_id + 1

        if update.message:
            today = date.today().strftime("%d_%m_%Y_")
            try:
                group_name = update.message.chat.title.replace(" ", "_")
            except ValueError:
                group_name = update.message.from_user.first_name
            message = update.message.text
            user = update.message.from_user.first_name
            with open(os.path.join('archives', today + group_name + '.txt'), "a+") as f:
                f.write(user + ': ' + message + '\n')


if __name__ == '__main__':
    main()