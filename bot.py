from telegram.ext import Updater
from telegram import BotCommandScopeAllPrivateChats, BotCommand, BotCommandScopeAllGroupChats
from config import update_info, webhook_info, Mongo, dev
from castpod.handlers import register_handlers
from castpod.models import Podcast
# from castpod.stats import register as register_stats
from mongoengine import connect
import datetime
updater = Updater(**update_info)
dispatcher = updater.dispatcher

# Use this method to logout your bot from telegram api:
# updater.bot.log_out()

# updater.bot.delete_webhook()
# updater.bot.close()

# Webhook:
updater.start_webhook(**webhook_info)  # Webhook

connection = dispatcher.run_async(
    connect,
    db=Mongo.db
    # username=Mongo.user, # for auth
    # password=Mongo.pwd # for auth
    # host=Mongo.remote_host # for remote test
)

register_handlers(dispatcher)
# register_stats(dispatcher) # stats


def make_job(i):
    def job(context):
        podcasts = Podcast.objects(job_group=i)
        # context.bot.send_message(dev, f'`{podcasts}`')
        for podcast in podcasts:
            podcast.check_update(context)
    return job


for i in range(48):
    interval = 15
    time = datetime.time(hour=i // (60 // interval), minute=i * interval % 60)
    dispatcher.job_queue.run_daily(
        make_job(i), time, name=f'update_podcast_group_{i}')

if connection.result():
    print('MongoDB Connected!')
else:
    raise Exception('MongoDB Connection Failed.')


updater.bot.set_my_commands(
    commands=[BotCommand('favorite', '我的单集收藏')], scope=BotCommandScopeAllGroupChats())

updater.bot.set_my_commands(commands=[
    BotCommand('search', '发现播客'),
    BotCommand('manage', '订阅管理'),
    BotCommand('star', '播客收藏'),
    BotCommand('favorite', '单集收藏'),
    BotCommand('share', '分享播客'),
    BotCommand('invite', '邀请好友'),
    BotCommand('bonus', '我的积分'),
    BotCommand('settings', '偏好设置'),
    BotCommand('help', '使用指南'),
    BotCommand('about', '关于…')
], scope=BotCommandScopeAllPrivateChats())

# Polling:
# updater.start_polling()  # polling

updater.idle()
