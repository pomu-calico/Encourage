import os
from slack_bolt import App
from praise_handler import register_praise_handlers
from countdown_handler import register_countdown_handlers

# Slack App 初期化
app = App(
    token=os.environ.get("SLACK_BOT_TOKEN"),
    signing_secret=os.environ.get("SLACK_SIGNING_SECRET")
)

IS_TEST = True#称賛機能テスト：Trueの場合テスト用チャンネルに
if IS_TEST:
    REFERRAL_CHANNEL_ID = "C095PR2DE0P"  # テスト用
    PRAISE_CHANNEL_ID = "C0965SZNRPW"    # テスト用
else:
    REFERRAL_CHANNEL_ID = "C0855QUNLUT"  # 本番用
    PRAISE_CHANNEL_ID = "C0979LVFSE8"    # 本番用


# 称賛機能を登録
register_praise_handlers(app,REFERRAL_CHANNEL_ID, PRAISE_CHANNEL_ID)

# カウントダウン機能を登録
register_countdown_handlers(app)

if __name__ == "__main__":
    app.start(port=int(os.environ.get("PORT", 3000)))
