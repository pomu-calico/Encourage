import os
import re
from flask import Flask, request
from slack_bolt import App
from slack_bolt.adapter.flask import SlackRequestHandler

from praise_handler import register_praise_handlers
from countdown_handler import register_countdown_handlers, send_countdowns

# -------------------------
# Slack App 初期化
# -------------------------
app = App(
    token=os.environ.get("SLACK_BOT_TOKEN"),
    signing_secret=os.environ.get("SLACK_SIGNING_SECRET")
)

IS_TEST = False  # 称賛機能テスト：Trueの場合テスト用チャンネルに
if IS_TEST:
    REFERRAL_CHANNEL_ID = "C095PR2DE0P"  # テスト用
    PRAISE_CHANNEL_ID = "C0965SZNRPW"    # テスト用
else:
    REFERRAL_CHANNEL_ID = "C0855QUNLUT"  # 本番用
    PRAISE_CHANNEL_ID = "C0979LVFSE8"    # 本番用

# 称賛機能を登録
register_praise_handlers(app, REFERRAL_CHANNEL_ID, PRAISE_CHANNEL_ID)

# カウントダウン機能を登録
register_countdown_handlers(app)

# -------------------------
# Flask アプリ設定
# -------------------------
flask_app = Flask(__name__)
handler = SlackRequestHandler(app)

# Slack Events API 用エンドポイント
@flask_app.route("/slack/events", methods=["POST"])
def slack_events():
    return handler.handle(request)

# 外部から叩ける手動トリガー (cron-job.org や Render Cron から)
@flask_app.route("/trigger_countdown", methods=["GET"])
def trigger_countdown():
    send_countdowns()
    return "Countdown executed!", 200

# -------------------------
# ローカル実行用
# -------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 3000))
    flask_app.run(host="0.0.0.0", port=port)