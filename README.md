# Castpod

> v0.1.1

一个 [Telegram 机器人](https://core.telegram.org/bots/api)。点击[链接](https://t.me/castpodbot)开始使用吧！
（项目仍处于初期阶段，亟待完善。）

## 基本

点击 `开始` 以启动机器人，所有的交互在对话框之间完成。

### 指令
点击文本输入框一旁的 `/` 可以唤出指令。主要指令如下：
- `/manage`：管理已订阅的播客
- `/help`：帮助与指南

使用 `/help` 后，弹出的其他指令：
- `/about`：关于本机器人与作者
- `/setting`：偏好设置
- `/export`：导出订阅文件
- `/logout`：注销账号并**清空**所有数据

### 导入播客
1. 直接发送订阅源文件（XML/OPML）以批量订阅；
2. 发送播客的 RSS 订阅地址（XML）

### 订阅、收听与管理
1. 启动机器人之后，点击 `搜索播客` 按钮，或者输入 `@` 找到 `@castpodbot`，输入关键字即可搜索播客并订阅。
2. 订阅之后，点击 `分集列表` 选择节目下载收听。
3. 同第一步，输入 `@castpodbot`，在不输入关键字的情况下，这里陈列着全部已订阅的播客。

## 部署

如果您有一点技术背景，可以考虑自己部署这个机器人，这样可以减少我们服务器的压力，同时带给您更流畅的使用体验。

### 安装依赖

使用 `python -m pip install -r requirements.txt` 安装所有依赖。

### 配置

在根目录新建一个配置文件 `config.ini` ，填写所需的变量。
```config.ini
[BOT]
TOKEN_TEST = 机器人测试token，可选。
TOKEN = 机器人token，找 @BotFather 领取
PROXY = 本地测试代理 http 链接，避开网路封锁
API = 自部署的 telegram-bot-api 地址，播客文件一般较大，如果不自己部署会超出 Telegram 的传输限制。
PODCAST_VAULT = Telegram「播客广场」的频道ID，即@后面的内容。这与本机器人的播客分发模式有关，可能不太好理解。

[WEBHOOK]
PORT = Webhook 端口数字，不使用请无视

[DEV]
USER_ID = 开发者（您）的 Telegram ID，整数。

[MONGODB]
USER = 用户名，可选
PWD = 密码，可选
DB_NAME = 数据库的名字
REMOTE_HOST = 服务器IP，用于本地测试（但并不安全），可选。
```
### 数据库
安装 MongoDB，运行 `mongod`。

### Polling v.s Webhook
[Webhook](https://github.com/python-telegram-bot/python-telegram-bot/wiki/Webhooks) 和 Polling 两种方法择其一，**建议从 Polling 直接上手**，无需更多配置。

在 `bot.py` 文件中注释掉含 #webhook 的**两条语句**、取消注释含 polling 的**两条语句**即可。

### 部署 Telegram Bot API
得益于近日 Bot API 已经开源，现在我们可以自己部署一个 Bot API。这是因为播客音频往往比较大，超出了 Telegram 的上传限制，所以需要自行部署。

关于如何部署，请参考 Telegram 的[官方部署指南](https://tdlib.github.io/telegram-bot-api/build.html)。

### 运行
- 直接运行： `python bot.py`
- 推荐使用进程管理器运行，如 [PM2](https://pm2.keymetrics.io/docs/usage/pm2-doc-single-page/) ：`pm2 start bot.py --name castpod --interpreter python --kill-timeout 3000`

## 支持本项目

### 文档支持
帮助我们填写[资料库](https://github.com/dahawong/castpod/wiki)。文档填写进度详见[文档书写](https://github.com/DahaWong/castpod/projects/5)

### 技术支持
> 我们熟悉 Telegram 的生态，但对 Python 特性与数据库相关处理并不熟练，代码亟待优化。欢迎提供建议/学习资源/PR

更多信息请参见[开发行程](https://github.com/DahaWong/castpod/projects/2)、[项目漏洞](https://github.com/DahaWong/castpod/projects/3)

### 经济支持
1. [爱发电](https://afdian.net/@castpodbot)
2. [Buy me a coffee](https://www.buymeacoffee.com/daha)

<a href="https://www.buymeacoffee.com/daha"><img src="https://img.buymeacoffee.com/button-api/?text=Buy me a Cherry  : )&emoji=🍒&slug=daha&button_colour=FF5F5F&font_colour=ffffff&font_family=Poppins&outline_colour=000000&coffee_colour=FFDD00"></a>
