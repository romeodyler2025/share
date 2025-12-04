import os
import asyncio
import random
from pyrogram import Client

# Config (Secret ထဲကနေ ယူပါမယ်)
API_ID = int(os.environ["API_ID"])
API_HASH = os.environ["API_HASH"]
SESSION = os.environ["SESSION_STRING"]
FROM_CH = int(os.environ["FROM_CHANNEL"])
TO_GP = int(os.environ["TO_GROUP"])

# တစ်ခါ Run ရင် ပို့မည့် အရေအတွက်
BATCH_SIZE = 3 

async def main():
    # GitHub Actions မို့လို့ in_memory=True ထားရပါမယ်
    app = Client("my_bot", api_id=API_ID, api_hash=API_HASH, session_string=SESSION, in_memory=True)
    
    async with app:
        print("🤖 Bot Started Checking...")

        # ၁. ပို့ပြီးသား ID တွေကို ဖတ်မယ်
        posted_ids = set()
        if os.path.exists("posted_ids.txt"):
            with open("posted_ids.txt", "r") as f:
                content = f.read().strip()
                if content:
                    # ကော်မာ (,) ခံပြီး သိမ်းထားလို့ ပြန်ခွဲထုတ်မယ်
                    posted_ids = set(int(x) for x in content.split(",") if x.isdigit())

        # ၂. Channel ထဲက နောက်ဆုံး Post ၁၀၀ ကို ဆွဲထုတ်မယ် (အဲ့ထဲကမှ Random ရွေးမယ်)
        # limit=100 ကို လိုသလို ပြောင်းလို့ရပါတယ်
        candidates = []
        async for msg in app.get_chat_history(FROM_CH, limit=200):
            # Video ဖြစ်ရမယ် + အရင်က မပို့ရသေးတဲ့ ID ဖြစ်ရမယ်
            if msg.video and msg.id not in posted_ids:
                candidates.append(msg)
        
        if not candidates:
            print("❌ No new videos found to share.")
            return

        # ၃. Random ၃ ပုဒ် ရွေးမယ်
        # ရှိတာက ၃ ပုဒ်အောက် နည်းနေရင် ရှိသလောက်ပဲ ယူမယ်
        pick_count = min(len(candidates), BATCH_SIZE)
        selected_msgs = random.sample(candidates, pick_count)

        # ၄. Forward (Copy) လုပ်မယ်
        newly_posted = []
        for msg in selected_msgs:
            try:
                print(f"📤 Forwarding Video ID: {msg.id}")
                
                # msg.copy က Caption (Review) ပါ တစ်ခါတည်း ပါပြီးသားပါ
                await msg.copy(TO_GP) 
                
                newly_posted.append(str(msg.id))
                await asyncio.sleep(5) # FloodWait ရှောင်ရန်
            except Exception as e:
                print(f"⚠️ Error on ID {msg.id}: {e}")

        # ၅. ပို့ပြီးသား ID တွေကို posted_ids.txt ထဲ ထပ်ဖြည့်မယ်
        if newly_posted:
            with open("posted_ids.txt", "a") as f:
                # မရှိသေးရင် ဒီတိုင်းရေး၊ ရှိရင် ကော်မာခံပြီး ရေး
                if os.path.getsize("posted_ids.txt") > 0:
                    f.write("," + ",".join(newly_posted))
                else:
                    f.write(",".join(newly_posted))
            print(f"✅ Saved {len(newly_posted)} new IDs to history.")

if __name__ == "__main__":
    app = Client("bot", api_id=API_ID, api_hash=API_HASH, session_string=SESSION)
    app.run(main())
