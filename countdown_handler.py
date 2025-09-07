from slack_bolt import App
from slack_sdk.errors import SlackApiError
from apscheduler.schedulers.background import BackgroundScheduler
import datetime
import os
import json
import re

DATA_FILE = "events.json"

# --- イベント保存・読み込み ---
def load_events():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_events(events):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(events, f, ensure_ascii=False, indent=2)

# --- イベント登録 ---
def register_countdown_handlers(app: App):
    @app.message(re.compile(r"(\d{4}-\d{2}-\d{2})\s+(.+?)\s+<#(C\w+)\|.*>"))
    def register_event(message, say, context):
        date_str = context['matches'][0]   # 期日
        event_name = context['matches'][1] # イベント名
        channel_id = context['matches'][2] # チャンネルID

        try:
            target_date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            say("❌ 日付フォーマットが正しくないよ（例: 2025-09-30 Hackathon #general）")
            return

        events = load_events()
        events.append({
            "date": date_str,
            "event_name": event_name,
            "channel": channel_id
        })
        save_events(events)

        say(f"✅ イベントを登録したよ！ {event_name} ({date_str}) in <#{channel_id}>")

    # --- イベント削除 ---
    @app.message(re.compile(r"^delete\s+(.+)$"))
    def delete_event(message, say, context):
        event_name = context['matches'][0].strip()
        events = load_events()
        new_events = [e for e in events if e["event_name"] != event_name]

        if len(new_events) == len(events):
            say(f"⚠️ '{event_name}' は見つからなかったよ。")
        else:
            save_events(new_events)
            say(f"🗑️ イベント '{event_name}' を削除したよ！")

    # --- 登録済みイベント一覧 ---
    @app.message("list")
    def list_events(message, say):
        events = load_events()
        if not events:
            say("📂 登録されているイベントはないよ。")
            return

        reply = "📅 登録済みイベント一覧:\n"
        for e in events:
            reply += f"- {e['event_name']} ({e['date']}) → <#{e['channel']}>\n"
        say(reply)

    # --- 毎日8時にカウントダウン送信 ---
    def send_countdowns():
        today = datetime.date.today()
        events = load_events()
        for event in events:
            target_date = datetime.datetime.strptime(event["date"], "%Y-%m-%d").date()
            days_left = (target_date - today).days
            if days_left >= 0:
                if days_left % 7 == 0:
                    message = f"<!channel> ⏳ {event['event_name']} まであと {days_left}日! あと{days_left // 7}週間だネ！！！"
                elif days_left == 1:
                    message = f"<!channel> ⏳ {event['event_name']} は明日!!!"
                else:
                    message = f"<!channel> ⏳ {event['event_name']} まであと {days_left}日!!!!!!!"
                try:
                    app.client.chat_postMessage(
                        channel=event["channel"],
                        text=message
                    )
                except SlackApiError as e:
                    print("Slack API エラー:", e)

    # --- スケジューラ設定 ---
    scheduler = BackgroundScheduler(timezone="Asia/Tokyo")
    scheduler.add_job(send_countdowns, "cron", hour=8, minute=00)  # 毎日8時
    scheduler.start()
