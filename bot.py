import os
from slack_bolt import App
from praise_handler import register_praise_handlers
from countdown_handler import register_countdown_handlers

# Slack App 初期化
app = App(
    token=os.environ.get("SLACK_BOT_TOKEN"),
    signing_secret=os.environ.get("SLACK_SIGNING_SECRET")
)

# 称賛機能を登録
register_praise_handlers(app)

# カウントダウン機能を登録
register_countdown_handlers(app)

if __name__ == "__main__":
    app.start(port=int(os.environ.get("PORT", 3000)))
