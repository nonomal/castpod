import datetime
import feedparser
import socket
import random

from telegram.parsemode import ParseMode
from castpod.utils import local_download
from config import podcast_vault, dev_user_id, manifest
from base64 import urlsafe_b64encode as encode
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import socket
import datetime
import re
import feedparser
from telegraph import Telegraph
from html import unescape


class User(object):
    """
    A Telegram User.
    """

    def __init__(self, name, user_id):
        self.name = name
        self.user_id = user_id
        self.subscription = {}
        self.subscription_path = f"./public/subscriptions/{self.user_id}.xml"

    def import_feeds(self, podcasts):
        for podcast in podcasts:
            self.add_feed(podcast)
        return self.subscription

    def add_feed(self, podcast):
        self.subscription.update({podcast.name: Feed(podcast)})
        return self.subscription

    def update_opml(self) -> str:
        body = ''
        for feed in self.subscription.values():
            podcast = feed.podcast
            outline = f'\t\t\t\t<outline type="rss" text="{podcast.name}" xmlUrl="{podcast.feed_url}"/>\n'
            body += outline
        head = (
            "<?xml version='1.0' encoding='UTF-8' standalone='yes' ?>\n"
            "\t<opml version='1.0'>\n"
            "\t\t<head>\n"
            f"\t\t\t<title>{manifest.name} 订阅源</title>\n"
            "\t\t</head>\n"
            "\t\t<body>\n"
            "\t\t\t<outline text='feeds'>\n"
        )
        tail = (
            "\t\t\t</outline>\n"
            "\t\t</body>\n"
            "\t</opml>\n"
        )
        opml = head + body + tail
        with open(self.subscription_path, 'w+') as f:
            f.write(opml)
        return self.subscription_path


class Podcast(object):
    def __init__(self, feed_url):
        self.feed_url = feed_url
        # self.id = uuid5(NAMESPACE_URL, feed_url)
        self.parse_feed(feed_url)
        self.subscribers = set()
        self.set_job_group()

    def parse_feed(self, url):
        socket.setdefaulttimeout(5)
        result = feedparser.parse(url)
        if str(result.status)[0] != '2' and str(result.status)[0] != '3':
            raise Exception(f'Feed URL Open Error, status: {result.status}')
        feed = result.feed
        self.name = feed.get('title')
        if not self.name:
            raise Exception("Cannot parse feed name.")
        self.name = unescape(self.name)[:32]
        if len(self.name) == 32:
            self.name += '…'
        self.logo_url = feed.get('image').get('href')
        # self.download_logo()
        self.episodes = self.set_episodes(result['items'])
        self.latest_episode = self.episodes[0]
        self.host = unescape(feed.author_detail.name)
        if self.host == self.name:
            self.host = ''
        self.website = feed.link
        self.email = feed.author_detail.get('email') or ""

    def set_job_group(self):
        i = random.randint(0,47)
        self.job_group = [i % 48 for i in range(i, i + 41, 8)]

    def update(self, context):
        last_published_time = self.latest_episode.published_time
        self.parse_feed(self.feed_url)
        if self.latest_episode.published_time != last_published_time:
            try:
                audio_file = local_download(self.latest_episode, context)
                encoded_podcast_name = encode(
                    bytes(self.name, 'utf-8')).decode("utf-8")
                audio_message = context.bot.send_audio(
                    chat_id=f'@{podcast_vault}',
                    audio=audio_file,
                    caption=(
                        f"<b>{self.name}</b>\n"
                        f"总第 {len(self.episodes)} 期\n\n"
                        f"<a href='https://t.me/{manifest.bot_id}?start={encoded_podcast_name}'>订阅</a> | "
                        f"<a href='{self.latest_episode.get_shownotes_url()}'>相关链接</a>"
                    ),
                    title=self.latest_episode.title,
                    performer=f"{self.name} | {self.latest_episode.host or self.host}" if self.host else self.name,
                    duration=self.latest_episode.duration.seconds,
                    thumb=self.logo_url,
                    parse_mode = ParseMode.HTML
                    # timeout = 1800
                )
                self.latest_episode.message_id = audio_message.message_id
                for user_id in self.subscribers:
                    forwarded_message = context.bot.forward_message(
                        chat_id=user_id,
                        from_chat_id=f"@{podcast_vault}",
                        message_id=self.latest_episode.message_id
                    )
                    forwarded_message.edit_caption(
                        caption=(
                            f"🎙️ *{self.name}*\n\n[相关链接]({self.latest_episode.get_shownotes_url() or self.website})"
                            f"\n\n{self.latest_episode.timeline}"
                        ),
                        reply_markup=InlineKeyboardMarkup([[
                            InlineKeyboardButton(
                                text="评     论     区",
                                url=f"https://t.me/{podcast_vault}/{audio_message.message_id}")
                        ], [
                            InlineKeyboardButton(
                                "订  阅  列  表", switch_inline_query_current_chat=""),
                            InlineKeyboardButton(
                                "单  集  列  表", switch_inline_query_current_chat=f"{self.name}")
                        ]]
                        )
                    )
            except Exception as e:
                context.bot.send_message(
                    dev_user_id, f'{context.job.name} 更新出错：`{e}`')

    def set_episodes(self, results):
        episodes = []
        for episode in results:
            episodes.append(Episode(self.name, episode, self.logo_url))
        return episodes

    # def download_logo(self):
    #     infile = f'public/logos/{self.name}.jpg'
    #     with open(infile, 'wb') as f:
    #         response = requests.get(
    #             self.logo_url, allow_redirects=True, stream=True)
    #         if not response.ok:
    #             raise Exception("URL Open Error: can't get this logo.")
    #         for block in response.iter_content(1024):
    #             if not block:
    #                 break
    #             f.write(block)
    #     self.logo = infile
    #     # outfile = os.path.splitext(infile)[0] + ".thumbnail.jpg"
    #     # try:
    #     #     with Image.open(infile) as im:
    #     #         im.thumbnail(size=(320, 320))
    #     #         im.convert('RGB')
    #     #         im.save(outfile, "JPEG")
    #     #     self.thumbnail = outfile
    #     # except Exception as e:
    #     #     print(e)
    #     #     self.thumbnail = ''


class Episode(object):
    """
    Episode of a specific podcast.
    """

    def __init__(self, from_podcast: str, episode, podcast_logo):
        self.podcast_name = from_podcast
        self.podcast_logo = podcast_logo
        self.host = unescape(episode.get('author')) or ''
        if self.host == from_podcast:
            self.host = ''
        self.audio = self.set_audio(episode.enclosures)
        if self.audio:
            self.audio_url = self.audio.href
            self.audio_size = self.audio.get('length') or 0
        else:
            self.audio_url = ""
            self.audio_size = 0
        self.title = self.set_title(episode.get('title'))
        self.subtitle = unescape(episode.get('subtitle') or '')
        if self.title == self.subtitle:
            self.subtitle = ''
        self.logo_url = episode.get(
            'image').href if episode.get('image') else ''
        self.duration = self.set_duration(episode.get('itunes_duration'))
        self.content = episode.get('content')
        self.summary = unescape(episode.get('summary') or '')
        self.shownotes = self.set_shownotes()
        self.timeline = self.set_timeline()
        self.shownotes_url = ''
        self.published_time = episode.published_parsed
        self.message_id = None

    def set_duration(self, duration: str) -> int:
        duration_timedelta = None
        if duration:
            if ':' in duration:
                time = duration.split(':')
                if len(time) == 3:
                    duration_timedelta = datetime.timedelta(
                        hours=int(time[0]),
                        minutes=int(time[1]),
                        seconds=int(time[2])
                    )
                elif len(time) == 2:
                    duration_timedelta = datetime.timedelta(
                        hours=0,
                        minutes=int(time[0]),
                        seconds=int(time[1])
                    )
            else:
                duration_timedelta = datetime.timedelta(seconds=int(duration))
        else:
            duration_timedelta = datetime.timedelta(seconds=0)
        return duration_timedelta

    def set_audio(self, enclosure):
        if enclosure:
            return enclosure[0]
        else:
            return None

    def set_title(self, title):
        if not title:
            return ''
        return unescape(title).lstrip(self.podcast_name)

    def set_shownotes(self):
        shownotes = unescape(self.content[0]['value']) if self.content else self.summary
        img_content = f"<img src='{self.logo_url or self.podcast_logo}'>" if 'img' not in shownotes else ''
        return img_content + self.replace_invalid_tags(shownotes)

    def set_timeline(self):
        shownotes = re.sub(r'</?(?:br|p|li).*?>', '\n', self.shownotes)
        # self.shownotes = re.sub(r'(?<=:[0-5][0-9])[\)\]\}】」）》>]+', '', self.shownotes)
        # self.shownotes = re.sub(r'[\(\[\{【「（《<]+(?=:[0-5][0-9])', '', self.shownotes)
        pattern = r'.+(?:[0-9]{1,2}:)?[0-9]{1,3}:[0-5][0-9].+'
        matches = re.finditer(pattern, shownotes)
        return '\n\n'.join([re.sub(r'</?(?:cite|del|span|div|s).*?>', '', match[0].lstrip()) for match in matches])

    def replace_invalid_tags(self, html_content):
        html_content = html_content.replace('h1', 'h3').replace('h2', 'h4')
        html_content = html_content.replace('cite>', "i>")
        html_content = re.sub(r'</?(?:div|span|audio).*?>', '', html_content)
        html_content = html_content.replace('’', "'")
        return html_content

    def get_shownotes_url(self):
        if self.shownotes_url:
            return self.shownotes_url

        telegraph = Telegraph()
        telegraph.create_account(
            short_name=manifest.name,
            author_name=manifest.name,
            author_url=f'https://t.me/{manifest.bot_id}'
        )

        res = telegraph.create_page(
            title=f"{self.title}",
            html_content=self.shownotes,
            author_name=self.host or self.podcast_name
        )
        self.shownotes_url = f"https://telegra.ph/{res['path']}"
        return self.shownotes_url


class Feed(object):
    """
    Feed of each user subscription.
    """

    def __init__(self, podcast):
        self.podcast = podcast
        self.is_latest = False
        self.is_saved = False
        self.audio_path = f'public/audio/{podcast.name}/'