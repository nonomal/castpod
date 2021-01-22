from utils.api_method import search
from telegram import InlineQueryResultArticle, InputTextMessageContent, InlineKeyboardButton, InlineKeyboardMarkup
import re
from uuid import uuid4


def handle_inline_query(update, context):
    query = update.inline_query
    query_text = query.query
    podcasts_match = re.match('^p (.*)', query_text)
    episodes_match = re.match('^e (.*)', query_text)
    results, kwargs = [], {"auto_pagination": True, "cache_time": 90}
    if not query_text:
        results, kwargs = welcome(context)
    elif podcasts_match:
        keyword = podcasts_match[1]
        results = search_saved(
            'podcasts', keyword, context) if keyword else show_saved('podcasts', context)
    elif episodes_match:
        keyword = episodes_match[1]
        results = search_saved(
            'episodes', keyword, context) if keyword else show_saved('episodes', context)
    else:
        podcasts = context.bot_data['podcasts']
        podcast = podcasts.get(query_text)
        if podcast:
            results = show_episodes(podcast)
        else:
            results = search_podcast(query_text)
        kwargs.update({"cache_time": 600})

    query.answer(
        results,
        **kwargs
    )

    return 0


def welcome(context):
    if not context.user_data.get('user'):
        results = []
        kwargs = {
            "switch_pm_text": "登录",
            "switch_pm_parameter": "login",
            "cache_time": 0
        }
    else:
        results = show_subscription(context)
        kwargs = {}
    return results, kwargs


def show_episodes(podcast):
    episodes = podcast.episodes
    buttons = [
        InlineKeyboardButton("订阅列表", switch_inline_query_current_chat=""),
        InlineKeyboardButton(
            "单集列表", switch_inline_query_current_chat=f"{podcast.name}")
    ]
    results = [InlineQueryResultArticle(
        id=index,
        title=episode.title,
        input_message_content=InputTextMessageContent((
            f"[🎙️]({podcast.logo_url}) *{podcast.name}* #{len(episodes) - index}"
        )),
        reply_markup=InlineKeyboardMarkup.from_row(buttons),
        description=f"{episode.duration or podcast.name}\n{episode.subtitle}",
        thumb_url=podcast.logo_url,
        thumb_width=60,
        thumb_height=60
    ) for index, episode in enumerate(episodes)]
    return results


def search_podcast(keyword):
    searched_results = search(keyword)
    listed_results = []
    if not searched_results:
        listed_results = [
            InlineQueryResultArticle(
                id='0',
                title="没有找到相关的播客呢 :(",
                description="换个关键词试试",
                input_message_content=InputTextMessageContent("🔍️"),
                reply_markup=InlineKeyboardMarkup.from_button(
                    InlineKeyboardButton(
                        '返回搜索', switch_inline_query_current_chat=keyword)
                )
            )
        ]
    else:
        for result in searched_results:
            name = re.sub(r"[_*`]", ' ', result['collectionName'])
            host = re.sub(r"[_*`]", ' ', result['artistName'])
            feed = result['feedUrl']
            thumbnail_small = result['artworkUrl60']

            # 如果不在 机器人主页，则：
            # [InlineKeyboardButton('前  往  B O T', url = f"https://t.me/{manifest.bot_id}")],

            result_item = InlineQueryResultArticle(
                id=result['collectionId'],
                title=name,
                input_message_content=InputTextMessageContent(feed, parse_mode=None),
                description=host,
                thumb_url=thumbnail_small,
                thumb_height=60,
                thumb_width=60
            )
            listed_results.append(result_item)
    return listed_results


def show_subscription(context):
    subscription = context.user_data['user'].subscription
    results = [InlineQueryResultArticle(
        id=index,
        title=feed.podcast.name,
        input_message_content=InputTextMessageContent(feed.podcast.name, parse_mode=None),
        description=feed.podcast.host or feed.podcast.name,
        thumb_url=feed.podcast.logo_url,
        thumb_width=60,
        thumb_height=60
    ) for index, feed in enumerate(subscription.values())]
    return results


def show_trending(context):
    user = context.user_data['user']
    podcasts = context.bot_data['podcasts']
    results = [InlineQueryResultArticle(
        id=uuid4(),
        title=podcast.name,
        description=podcast.host or podcast.name,
        input_message_content=InputTextMessageContent((
            f"{podcast.feed_url}"
        )),
        # reply_markup = InlineKeyboardMarkup(),
        thumb_url=podcast.logo_url,
        thumb_width=60,
        thumb_height=60
    ) for podcast in podcasts.values() if not user.subscription.get(podcast.name)]
    return results


def search_saved(saved_type, keyword):
    pass


def show_saved(saved_type):
    pass
