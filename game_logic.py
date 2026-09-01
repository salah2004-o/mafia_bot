# game_logic.py
import random

class MafiaGame:
    EVENT_POOL = [
        {
            "title": "ظلال القصر",
            "description": "كانت السماء تشتعل في الأفق بينما تنبعث أصوات همسات في أزقة المدينة.",
            "image": "event_castle"
        },
        {
            "title": "ليلة الضباب الكثيف",
            "description": "يخيم الضباب على الشوارع، لتزداد المخاطر وتصبح القرارات أكثر صعوبة.",
            "image": "event_fog"
        },
        {
            "title": "نداء الحاكم",
            "description": "يا أهل المدينة، تم التحذير من وجود خائن بيننا. الوقت للتصرف الآن.",
            "image": "event_mayor"
        },
        {
            "title": "رسائل مظلمة",
            "description": "وصلت أنباء عن رسالة مجهولة تكشف سرًا واحدًا. من سيصدق؟",
            "image": "event_letter"
        },
        {
            "title": "همسات السوق",
            "description": "ينتشر خبر قديم في السوق. البعض يعتقد أن المافيا تخطط لهجوم الليلة.",
            "image": "event_market"
        }
    ]

    def __init__(self, chat_id: int):
        self.chat_id = chat_id
        self.players = {}  # هيكل البيانات: {user_id: {"name": str, "role": str, "is_alive": bool}}
        self.phase = "join"  # join, night, voting
        self.round_number = 0
        self.story_history = []
        self.event_deck = []
        
        # قرارات الليل
        self.killed_target = None
        self.saved_target = None
        self.guarded_target = None
        self.silenced_target = None
        self.checked_target = None
        self.night_actions = {}
        # سجل فحص المحقق في الليلة السابقة (ليستخدمه المهندس)
        self.prev_detective_target = None
        
        # تصويت النهار
        self.votes = {}  # {voted_user_id: count}
        self.voted_already = set() # اللاعبين الذين صوتوا بالفعل
        # خريطة رشوة المصرفيين (bank_uid -> bribe_target_uid)
        self.bank_bribe_map = {}
        # حماية القاضي المستهدفة (يُحفظ هدف واحد يمكن حمايته مرة واحدة)
        self.judge_protect = None

    def add_player(self, user_id: int, name: str) -> bool:
        if user_id not in self.players:
            self.players[user_id] = {"name": name, "role": None, "is_alive": True}
            return True
        return False

    def distribute_roles(self):
        """توزيع الأدوار بناءً على الحد الأدنى (4 لاعبين على الأقل)"""
        uids = list(self.players.keys())
        random.shuffle(uids)
        # تحديد عدد المافيا ديناميكياً: تقريبا واحد لكل 4 لاعبين
        n = len(uids)
        mafia_count = max(1, n // 4)

        # اختر رؤوس المافيا أولاً
        mafia_uids = uids[:mafia_count]
        for uid in mafia_uids:
            self.players[uid]["role"] = "mafia"

        remaining = [uid for uid in uids if uid not in mafia_uids]

        # إذا توفرت لاعبين، عيّن طبيب ومحقق
        if len(remaining) >= 1:
            self.players[remaining[0]]["role"] = "doctor"
        if len(remaining) >= 2:
            self.players[remaining[1]]["role"] = "detective"
        if len(remaining) >= 3:
            self.players[remaining[2]]["role"] = "bodyguard"
        if len(remaining) >= 4:
            self.players[remaining[3]]["role"] = "silencer"
        if len(remaining) >= 5:
            self.players[remaining[4]]["role"] = "mayor"

        # إذا توفرت أدوار إضافية، عَيّنها بالتتابع
        extra_roles = ["trickster", "security", "judge", "engineer", "vendor", "bank", "addict", "traitor"]
        for i, uid in enumerate(remaining[5:]):
            if i < len(extra_roles):
                self.players[uid]["role"] = extra_roles[i]
            else:
                self.players[uid]["role"] = "civilian"

        # أضف حالة الاستخدام الافتراضية لكل لاعب للأدوار التي تعمل لمرة واحدة
        for uid, p in self.players.items():
            p.setdefault("uses", {})
            role = p.get("role")
            if role == "trickster":
                p["uses"]["trickster"] = 1
            if role == "security":
                p["uses"]["security"] = 1
            if role == "judge":
                p["uses"]["judge"] = 1
            if role == "bank":
                p["uses"]["bank"] = 1
            # default other roles may have ongoing abilities

        self.init_event_deck()

    def init_event_deck(self):
        self.event_deck = random.sample(self.EVENT_POOL, len(self.EVENT_POOL))

    def next_round_event(self):
        if not self.event_deck:
            self.init_event_deck()
        event = self.event_deck.pop(0)
        self.round_number += 1
        self.story_history.append(event)
        return event

    def get_alive_players(self):
        return {uid: p for uid, p in self.players.items() if p["is_alive"]}

    def process_night(self) -> str:
        """معالجة أحداث الليل وإرجاع اسم القتيل إن وجد"""
        killed = []

        # نفذ أولاً أفعال السرّاق/المحتال (trickster) - سرقة الدور
        for actor_uid, (role, target_uid) in list(self.night_actions.items()):
            if role == "trickster" and self.players.get(actor_uid, {}).get("uses", {}).get("trickster", 0) > 0:
                victim = self.players.get(target_uid)
                if victim and victim.get("is_alive", False):
                    victim_role = victim.get("role")
                    # المحتال يسرق دور الضحية، والضحية يصبح مواطناً
                    self.players[actor_uid]["role"] = victim_role
                    victim["role"] = "civilian"
                    self.players[actor_uid]["uses"]["trickster"] -= 1

        # نفذ أفعال الحارس/الأمن الذين يخرِجون لاعباً من اللعبة فوراً
        for actor_uid, (role, target_uid) in list(self.night_actions.items()):
            if role == "security" and self.players.get(actor_uid, {}).get("uses", {}).get("security", 0) > 0:
                target = self.players.get(target_uid)
                if target and target.get("is_alive", False):
                    target["is_alive"] = False
                    killed.append(target["name"])
                    self.players[actor_uid]["uses"]["security"] -= 1

        # جمع تصويت المافيا (أكثر الأهداف المحددة من قبل المافيا)
        mafia_votes = {}
        doctor_targets = []
        guard_targets = []
        for actor_uid, (role, target_uid) in self.night_actions.items():
            if role == "mafia":
                mafia_votes[target_uid] = mafia_votes.get(target_uid, 0) + 1
            if role == "doctor":
                doctor_targets.append(target_uid)
            if role == "bodyguard":
                guard_targets.append(target_uid)
            if role == "detective":
                # تخزين نتيجة فحص المحقق لتُستخدم لاحقًا
                self.prev_detective_target = target_uid
            if role == "silencer":
                self.silenced_target = target_uid
            if role == "judge" and self.players.get(actor_uid, {}).get("uses", {}).get("judge", 0) > 0:
                # قاضي يحدد هدفًا ليحميه من الطرد النهاري لاحقًا
                self.judge_protect = target_uid
                self.players[actor_uid]["uses"]["judge"] -= 1
            if role == "bank":
                # المصرفي يحدد من سيرشوه إن تم التصويت عليه (يُحفظ حسب معرف المصرفي)
                self.bank_bribe_map[actor_uid] = target_uid

        # حسم هدف المافيا الأكثر تصويتًا
        mafia_target = None
        if mafia_votes:
            mafia_target = max(mafia_votes, key=mafia_votes.get)

        # اختر هدف الطبيب (آخر اختيار إن وُجد)
        saved = doctor_targets[-1] if doctor_targets else None

        # إذا استهدفت المافيا شخصًا
        if mafia_target:
            # إذا الطبيب حمى الهدف
            if mafia_target == saved:
                pass  # لا أحد يموت
            elif mafia_target in guard_targets:
                # إذا الحارس حمى الهدف، يموت الحارس بدلًا منه
                # ابحث عن الحارس الحي الذي حمى هذا الهدف
                guard_uid = next((uid for uid, p in self.players.items() if p.get("role") == "bodyguard" and p.get("is_alive") and self.night_actions.get(uid, (None, None))[1] == mafia_target), None)
                if guard_uid:
                    self.players[guard_uid]["is_alive"] = False
                    killed.append(self.players[guard_uid]["name"])
                else:
                    self.players[mafia_target]["is_alive"] = False
                    killed.append(self.players[mafia_target]["name"])
            else:
                self.players[mafia_target]["is_alive"] = False
                killed.append(self.players[mafia_target]["name"])

        # إعادة تهيئة لقرارات الليل
        self.night_actions.clear()
        self.killed_target = None
        self.saved_target = None
        self.guarded_target = None
        self.silenced_target = None
        self.checked_target = None
        # ملاحظة: خريطة رشوة المصرفيين تبقى حتى استخدام الرشوة عند التصويت
        # إرجاع نص لعرضه في الدردشة
        if not killed:
            return "لا أحد"
        return ", ".join(killed)

    def process_voting(self) -> str:
        """معالجة التصويت النهاري وطرد اللاعب الأكثر تصويتاً"""
        if not self.votes:
            return "لم يصوت أحد، لم يُطرد أحد."
            
        max_votes = max(self.votes.values())
        targets = [uid for uid, count in self.votes.items() if count == max_votes]
        if len(targets) > 1:
            self.votes.clear()
            self.voted_already.clear()
            return "⚖️ تعادل الأصوات، لم يتم طرد أحد هذا اليوم."

        target_uid = targets[0]

        # تحقق إذا كان القاضي قد حمى هذا اللاعب
        if self.judge_protect == target_uid:
            # القاضي استخدم حمايته؛ ألغي الطرد
            self.judge_protect = None
            self.votes.clear()
            self.voted_already.clear()
            return f"⚖️ القاضي تدخل وأنقذ {self.players[target_uid]['name']} — لم يُطرد اليوم."

        # تحقق رشوة المصرفي: إذا كان الهدف مصرفيًا ولديه رشوة محددة
        target_player = self.players[target_uid]
        if target_player.get("role") == "bank" and target_player.get("uses", {}).get("bank", 0) > 0:
            bribe_target = self.bank_bribe_map.get(target_uid)
            if bribe_target and self.players.get(bribe_target, {}).get("is_alive", False):
                # المصرفي يستخدم رشوة ليُمحى مكانه
                self.players[bribe_target]["is_alive"] = False
                lynched_name = self.players[bribe_target]["name"]
                # استهلاك رشوة المصرفي
                target_player["uses"]["bank"] = 0
                # إزالة خريطة الرشوة
                self.bank_bribe_map.pop(target_uid, None)
                self.votes.clear()
                self.voted_already.clear()
                return f"🔥 نتيجة تصويت مفاجئ: {lynched_name} تم تنفيذ الإعدام بدلاً من {target_player['name']} (رشوة)."

        # الحالة الافتراضية: طرد الهدف
        self.players[target_uid]["is_alive"] = False
        lynched_name = self.players[target_uid]["name"]

        self.votes.clear()
        self.voted_already.clear()
        return f"🔥 قررت المدينة طرد: {lynched_name}"

    def check_game_over(self) -> str:
        """التحقق من شروط الفوز"""
        alive = self.get_alive_players()
        mafia_count = sum(1 for p in alive.values() if p["role"] == "mafia")
        civilian_count = len(alive) - mafia_count
        
        if mafia_count == 0:
            return "civilians"
        if mafia_count >= civilian_count:
            return "mafia"
        return None