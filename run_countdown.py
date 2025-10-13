import os
from countdown_handler import send_countdowns
from slack_bolt import App

# Slack App 初期化（Webサービスと同じ設定）
app = App(
    token=os.environ.get("SLACK_BOT_TOKEN"),
    signing_secret=os.environ.get("SLACK_SIGNING_SECRET")
)

if __name__ == "__main__":
    send_countdowns(app)