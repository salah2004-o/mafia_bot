# config.py

BOT_TOKEN = "8870268021:AAGQs_A3hwapLsOE7Lvev8HH7aQZ-0wpQLs"
CHANNEL_GROUP_ID = -1002628166858   # آيدي قناة القروب للاشتراك الإجباري
CHANNEL_DEV_ID = -1002193219929     # آيدي قناة المطور للاشتراك الإجباري
DEV_USERNAME = "@I_see_y_o_u"      # <--- أضف هذا المتغير
DB_PATH = "mafia_game.db"

# أوقات المراحل بالثواني (يمكنك تعديلها للتجربة)
REGISTRATION_TIME = 180  # 3 دقائق للتسجيل
NIGHT_TIME = 45          # 45 ثانية لاتخاذ القرارات بالخاص
DAY_TIME = 45            # 45 ثانية للنقاش والتصويت في العام

# روابط أو File IDs الصور الخاصة بكل حدث
IMAGES = {
    "start": "https://images.unsplash.com/photo-1509248961158-e54f6934749c", # صورة البداية
    "night": "https://images.unsplash.com/photo-1506703719100-a0f3a48c0f86", # حل الليل
    "day": "https://images.unsplash.com/photo-1470252649378-9c29740c9fa8",   # حل النهار
    "mafia_win": "https://images.unsplash.com/photo-1533738363-b7f9aef128ce", # فوز المافيا
    "civilians_win": "https://images.unsplash.com/photo-1541872703-74c5e44368f9" # فوز المواطنين
}

# صور إضافية لكل دور وإشعارات داخل اللعبة
IMAGES.update({
    "role_mafia": "https://images.unsplash.com/photo-1549887534-6d1b2f1b9a3b",
    "role_doctor": "https://images.unsplash.com/photo-1506794778202-cad84cf45f1d",
    "role_detective": "https://images.unsplash.com/photo-1524504388940-b1c1722653e1",
    "role_bodyguard": "https://images.unsplash.com/photo-1517841905240-472988babdf9",
    "role_silencer": "https://images.unsplash.com/photo-1499951360447-b19be8fe80f5",
    "role_mayor": "https://images.unsplash.com/photo-1517841905240-472988babdf9",
    "role_trickster": "https://images.unsplash.com/photo-1524503033411-c9566986fc8f",
    "role_security": "https://images.unsplash.com/photo-1529333166437-7750a6dd5a70",
    "role_judge": "https://images.unsplash.com/photo-1515191107209-c28698631303",
    "role_engineer": "https://images.unsplash.com/photo-1518770660439-4636190af475",
    "role_vendor": "https://images.unsplash.com/photo-1541529086526-2b8b6a1b8f6a",
    "role_bank": "https://images.unsplash.com/photo-1531379410501-4b8f7b49d6a6",
    "role_addict": "https://images.unsplash.com/photo-1511988617509-a57c8a288659",
    "role_traitor": "https://images.unsplash.com/photo-1524504388940-b1c1722653e1",
    "role_civilian": "https://images.unsplash.com/photo-1494790108377-be9c29b29330",
    "event_castle": "https://images.unsplash.com/photo-1500530855697-b586d89ba3ee",
    "event_fog": "https://images.unsplash.com/photo-1483721310020-03333e577078",
    "event_mayor": "https://images.unsplash.com/photo-1524504388940-b1c1722653e1",
    "event_letter": "https://images.unsplash.com/photo-1515378791036-0648a3ef77b2",
    "event_market": "https://images.unsplash.com/photo-1500534314209-a25ddb2bd429",
    "joined": "https://images.unsplash.com/photo-1515879218367-8466d910aaa4",
    "vote_confirm": "https://images.unsplash.com/photo-1508672019048-805c876b67e2",
    "eliminated": "https://images.unsplash.com/photo-1508685096483-4e0b0bbf6f3d"
})
