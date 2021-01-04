from telegram import InlineKeyboardButton, InlineKeyboardMarkup, error, ReplyKeyboardRemove, ChatAction
from base64 import urlsafe_b64encode as encode
from models import Episode
from config import podcast_vault
from utils.downloader import local_download as download
from manifest import manifest
import re

# Message
def delete_message(update, context):
    update.callback_query.delete_message()

def delete_command_context(update, context):
    pattern = r'(delete_command_context_)([0-9]+)'
    query = update.callback_query
    command_message_id = re.match(pattern, query.data)[2]
    query.delete_message()
    context.bot.delete_message(query.message.chat_id, command_message_id)

# Episode
def download_episode(update, context):
    bot = context.bot
    query = update.callback_query
    fetching_note = bot.send_message(query.from_user.id, "获取节目中，请稍候…")
    bot.send_chat_action(query.from_user.id, ChatAction.RECORD_AUDIO)
    pattern = r'download_episode_(.+)_([0-9]+)'
    match = re.match(pattern, query.data)
    podcast_name, index = match[1], int(match[2])
    podcast = context.bot_data['podcasts'][podcast_name]
    episode = podcast.episodes[index]
    if episode.audio_size and int(episode.audio_size) < 20000000:
        audio_message = direct_download(context, fetching_note, episode, podcast)
    else:
        audio_message = local_download(context, fetching_note, episode, podcast)
    forwarded_message = audio_message.forward(query.from_user.id)
    forwarded_message.edit_reply_markup(
        reply_markup=InlineKeyboardMarkup.from_button(
            InlineKeyboardButton(
                "评    论", 
                url=f"https://t.me/{podcast_vault}/{audio_message.message_id}"
            )
        )
    )

def direct_download(context, fetching_note, episode, podcast): 
    bot = context.bot
    # bot.send_chat_action(query.from_user.id, ChatAction.RECORD_AUDIO)
    promise = context.dispatcher.run_async(
        bot.send_audio,
        chat_id = f'@{podcast_vault}',
        audio = episode.audio_url,
        caption = f"#{podcast.name}",
        title = episode.title,
        performer = f"{podcast.name} - {episode.host or podcast.host}",
        duration = episode.duration.seconds,
        thumb = episode.logo_url or podcast.logo_url
    )
    if (promise.done):
        try:
            audio_message = promise.result()
            fetching_note.delete()
            return audio_message

        except error.BadRequest:
            return local_download(context, fetching_note, episode)

def local_download(context, fetching_note, episode, podcast):
    bot = context.bot
    chat_id = context.user_data['user'].user_id
    fetching_note.delete()
    try:
        file_path = download(episode.audio_url, context)
        # context.bot.send_chat_action(query.from_user.id, ChatAction.UPLOAD_AUDIO)
        encoded_podcast_name = encode(bytes(podcast.name, 'utf-8')).decode("utf-8")
        tagged_podcast_name = '#'+ re.sub(r'[\W]+', '_', podcast.name)
        audio_message = bot.send_audio(
            chat_id = f'@{podcast_vault}',
            audio = file_path,
            caption = (
                f"<b>{podcast.name}</b>"
                f"\n<a href='https://t.me/{manifest.bot_id}?start={encoded_podcast_name}'>订阅</a>"
                f"\n\n {tagged_podcast_name}"
            ),
            title = episode.title,
            performer = f"{episode.host or podcast.host}",
            duration = episode.duration.seconds,
            thumb = episode.logo_url or podcast.logo_url,
            timeout = 300,
            parse_mode = 'html'
        )
        return audio_message
    except Exception as e:
        print(e)

# Tips

def close_tips(update, context):
    query = update.callback_query
    pattern = r'close_tips_(\w+)'
    from_command = re.match(pattern, query.data)[1]
    context.user_data['tips'].remove(from_command)
    delete_message(update, context)
    show_tips_alert = 'alert' in context.user_data['tips']
    if show_tips_alert:
        query.answer("阅读完毕，它不会再出现在对话框中～", show_alert = True)
        context.user_data['tips'].remove('alert')

# Account:

def logout(update, context):
    user = context.user_data.get('user')
    message = update.callback_query.message
    message.edit_text(
        "注销账号之前，您可能希望导出订阅数据？",
        reply_markup = InlineKeyboardMarkup.from_row([
            InlineKeyboardButton("直 接 注 销", callback_data="delete_account"),
            InlineKeyboardButton("导 出 订 阅", callback_data="export")
        ])
    )

def delete_account(update, context):
    user = context.user_data['user']
    message = update.callback_query.message
    deleting_note = message.edit_text("注销中…")
    if user.subscription.values():
        for feed in user.subscription.values():
            if user.user_id in feed.podcast.subscribers:
                feed.podcast.subscribers.remove(user.user_id)
    context.user_data.clear()
    deleting_note.delete()
    success_note = context.bot.send_message(
        chat_id = user.user_id, 
        text = '您的账号已注销～', 
        reply_markup = ReplyKeyboardRemove())
    context.bot.send_message(
        chat_id = user.user_id, text = "👋️",
        reply_markup=InlineKeyboardMarkup.from_button(
            InlineKeyboardButton('重 新 开 始', url=f"https://t.me/{manifest.bot_id}?start=login")
    ))