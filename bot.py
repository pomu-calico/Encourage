import random
import re
import os
from slack_bolt import App
from slack_sdk.errors import SlackApiError

app = App(
    token=os.environ.get("SLACK_BOT_TOKEN"),
    signing_secret=os.environ.get("SLACK_SIGNING_SECRET")
)

IS_TEST = False#Trueの場合テスト用チャンネルに
if IS_TEST:
    REFERRAL_CHANNEL_ID = "C095PR2DE0P"  # テスト用
    PRAISE_CHANNEL_ID = "C0965SZNRPW"    # テスト用
else:
    REFERRAL_CHANNEL_ID = "C0855QUNLUT"  # 本番用
    PRAISE_CHANNEL_ID = "C0979LVFSE8"    # 本番用

ua_member_id =["U080YB72HJ9","U085FSU62CQ","U08HP59DVHA","U08UY4U3WC8","U090PFFT2MS"]#金井茉央,半田凌也,佐藤宏紀,板井一希,橋本歩武

@app.event("reaction_added")
def handle_reaction(event, client):
    reaction = event['reaction']
    channel_id = event['item']['channel']
    ts = event['item']['ts']
    user = event['user']

    # 条件1：チャンネル限定
    if channel_id != REFERRAL_CHANNEL_ID:
        return

    # 条件2：リアクションが「獲得」
    if reaction not in ["獲得", "獲得2", "獲得最高", "獲得キター"]:
        return

    try:
        # 対象メッセージ取得
        result = client.conversations_history(
            channel=channel_id,
            latest=ts,
            inclusive=True,
            limit=1
        )
        messages = result.get("messages", [])
        if not messages:
            print("メッセージが見つかりません")
            return

        original_message = messages[0]
        text = original_message.get("text", "")

        # 最初のメンション（<@U12345678>）を抽出
        mention_match = re.search(r"<@([A-Z0-9]+)>", text)
        if not mention_match:
            print("誰を称賛すれば良いかわかんないよ；；(条件を満たすメンション先が見つかりません)")
            return

        mentioned_user_id = mention_match.group(1)

        # メンションされたユーザーの表示名を取得
        user_info = client.users_info(user=mentioned_user_id)
        real_name = user_info["user"]["real_name"]

        # 元投稿をSlackの引用形式に整形（行ごとに > をつける
        quoted_text = "\n".join([f"> {line}" for line in text.strip().splitlines()])

        # 称賛メッセージを生成して送信
        praise_templates = [
    "🎉 <@{mentioned_user_id}> が獲得！みんな称賛の時間だああああああ！！！！\n",
    "🎉 <@{mentioned_user_id}> が獲得！頑張った人は褒められるべきだよね！？返信でガンガン讃えようぜ！\n",
    "👏 獲得情報！<@{mentioned_user_id}> の努力に拍手！\n",
    "🌟 <@{mentioned_user_id}> やるじゃん！獲得おめでとう！\n",
    "🔥 <@{mentioned_user_id}> がやったぜ！みんなで盛り上がろう！\n",
    "💪 獲得情報！<@{mentioned_user_id}> の活躍ヤバい！称賛の嵐だ！\n",
    "🥳 <@{mentioned_user_id}> 獲得おめでとう！最高のメンターだ！\n",
    "✨ <@{mentioned_user_id}> の努力が光ってる！みんな拍手！\n ",
    "🎊 やったね！<@{mentioned_user_id}> の偉業に乾杯！\n",
    "🌈 <@{mentioned_user_id}> が輝いてる！称賛メッセージ送ろうぜ！\n",
    "💥 <@{mentioned_user_id}> がリファ獲得！みんなで歓声あげよう！\n",
    "👏🏻 <@{mentioned_user_id}> がリファ獲得！マジで尊敬！\n",
    "🎖️ <@{mentioned_user_id}> の活躍は頼もしい！見習おう！\n",
    "🌟 <@{mentioned_user_id}> の獲得、みんなで称えよう！\n>",
    "🎉 <@{mentioned_user_id}> ナイスリファ！これからも期待してるぜ！\n>",
    "💫 <@{mentioned_user_id}> が獲得！最高のパフォーマンスを見せたあああああああ！\n",
    "🙌 <@{mentioned_user_id}> 獲得ほんとにお疲れ！みんな拍手！\n",
    "👏 <@{mentioned_user_id}> の努力に乾杯！一緒にがんばろうぜ！\n",
    "🎈 <@{mentioned_user_id}> 今日のヒーローだ！みんなで称えて盛り上がろうぜ！\n"
]

        # テンプレートを選び、メンション部分を埋め込む
        praise_user_id = random.choice(ua_member_id)
        praise_template = random.choice(praise_templates)
        formatted_template = praise_template.format(mentioned_user_id=mentioned_user_id)

        # 称賛メッセージを組み立て
        praise_message = (
            "リファ相談チャンネルに称賛スタンプが押されました！\n"
            f"~~称賛担当者~~\n<@{praise_user_id}>\n"
            f"~~称賛例~~\n{formatted_template}"
            f"~~スタンプが押された投稿~~\n{quoted_text}"
        )

        client.chat_postMessage(
            channel=PRAISE_CHANNEL_ID,
            text=praise_message
        )
        print(f"称賛メッセージを送信しました: {praise_message}")
        
    except SlackApiError as e:
        print(f"Slack API エラー: {e.response['error']}")
        print("エラー詳細:", e.response["error"])
        print("レスポンス全体:", e.response.data)
    except Exception as e:
            print("Slack API エラー:", e)

if __name__ == "__main__":
    app.start(port=int(os.environ.get("PORT", 3000)))
