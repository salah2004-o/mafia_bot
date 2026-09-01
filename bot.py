import logging
import os
import time
import threading
from typing import Optional
from dotenv import load_dotenv
import telebot
from telebot.apihelper import ApiTelegramException
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from services.database_service import DatabaseService
from services.logger_service import LoggerService
from services.statistics_manager import StatisticsManager
from models.player import Player
from models.session_manager import SessionManager
from models.role import RoleManager
from action_resolver import ActionResolver
from config import IMAGES, DEV_USERNAME
import images

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    try:
        from config import BOT_TOKEN as CONFIG_BOT_TOKEN
        BOT_TOKEN = CONFIG_BOT_TOKEN
    except Exception:
        pass

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN is required. Add it to .env, config.py, or set the environment variable before running bot.py.")

OWNER_IDS = [int(x.strip()) for x in os.getenv("OWNER_IDS", "").split(",") if x.strip()]
REGISTRATION_TIME_NORMAL = int(os.getenv("REGISTRATION_TIME_NORMAL", "90"))
NIGHT_TIME_NORMAL = int(os.getenv("NIGHT_TIME_NORMAL", "60"))
DAY_TIME_NORMAL = int(os.getenv("DAY_TIME_NORMAL", "120"))
REGISTRATION_TIME_QUICK = int(os.getenv("REGISTRATION_TIME_QUICK", "45"))
NIGHT_TIME_QUICK = int(os.getenv("NIGHT_TIME_QUICK", "30"))
DAY_TIME_QUICK = int(os.getenv("DAY_TIME_QUICK", "60"))
REGISTRATION_TIME_LONG = int(os.getenv("REGISTRATION_TIME_LONG", "180"))
NIGHT_TIME_LONG = int(os.getenv("NIGHT_TIME_LONG", "90"))
DAY_TIME_LONG = int(os.getenv("DAY_TIME_LONG", "240"))

class PollingExceptionHandler(telebot.ExceptionHandler):
    def handle(self, exception):
        if isinstance(exception, ApiTelegramException) and ("409" in str(exception) or "Conflict" in str(exception)):
            raise exception
        return False

bot = telebot.TeleBot(
    BOT_TOKEN,
    parse_mode="HTML",
    threaded=False,
    exception_handler=PollingExceptionHandler(),
)

_db_service = DatabaseService()
logger = LoggerService()
stats = StatisticsManager()
resolver = ActionResolver()
session_manager = SessionManager()

def get_image_source(image_key: str) -> Optional[str]:
    return images.get_image_source(image_key) or IMAGES.get(image_key)


def send_media(chat_id: int, image_key: str, caption: Optional[str] = None, reply_markup=None, parse_mode="HTML") -> None:
    image_source = get_image_source(image_key)
    if image_source:
        try:
            if os.path.isfile(image_source):
                with open(image_source, "rb") as photo:
                    bot.send_photo(chat_id, photo, caption=caption, reply_markup=reply_markup, parse_mode=parse_mode)
            else:
                bot.send_photo(chat_id, image_source, caption=caption, reply_markup=reply_markup, parse_mode=parse_mode)
            return
        except Exception:
            pass
    if caption is not None:
        bot.send_message(chat_id, caption, reply_markup=reply_markup, parse_mode=parse_mode)


def send_phase_countdown(chat_id: int, total_seconds: int, label: str) -> None:
    bot.send_message(chat_id, f"⏳ بدأ {label} لمدة {total_seconds} ثانية.")
    if total_seconds <= 10:
        time.sleep(total_seconds)
        return

    checkpoints = [60, 30, 10]
    remaining = total_seconds
    for marker in checkpoints:
        if remaining > marker:
            time.sleep(remaining - marker)
            remaining = marker
            bot.send_message(chat_id, f"⏳ {label} سينتهي بعد {marker} ثانية.")
    if remaining > 0:
        time.sleep(remaining)


SESSION_MODES = {
    "quick": (REGISTRATION_TIME_QUICK, NIGHT_TIME_QUICK, DAY_TIME_QUICK),
    "normal": (REGISTRATION_TIME_NORMAL, NIGHT_TIME_NORMAL, DAY_TIME_NORMAL),
    "long": (REGISTRATION_TIME_LONG, NIGHT_TIME_LONG, DAY_TIME_LONG),
}

active_sessions_lock = threading.RLock()
BOT_USERNAME = None


def get_bot_username() -> str:
    global BOT_USERNAME
    if BOT_USERNAME is None:
        BOT_USERNAME = bot.get_me().username
    return BOT_USERNAME


def build_inline_keyboard(rows):
    markup = InlineKeyboardMarkup()
    for row in rows:
        markup.row(*row)
    return markup


def is_owner(user_id: int, username: str | None = None) -> bool:
    if user_id in OWNER_IDS:
        return True
    if username and DEV_USERNAME:
        config_username = DEV_USERNAME.lstrip("@").lower()
        if username.lstrip("@").lower() == config_username:
            return True
    return False


def get_role_action_instructions(role):
    if not role.can_act_at_night:
        return "❌ ليس لديك قدرة ليلية."
    if role.key in {"godfather", "hitman", "deceiver", "impostor"}:
        return "📩 أرسل في الخاص: kill <اسم اللاعب> أو قتل <اسم اللاعب>"
    if role.key == "doctor":
        return "📩 أرسل في الخاص: save <اسم اللاعب> أو حمي <اسم اللاعب>"
    if role.key == "detective":
        return "📩 أرسل في الخاص: check <اسم اللاعب> أو تحقق <اسم اللاعب>"
    if role.key == "bodyguard":
        return "📩 أرسل في الخاص: guard <اسم اللاعب> أو احمِ <اسم اللاعب>"
    if role.key == "judge":
        return "📩 أرسل في الخاص: protect <اسم اللاعب> أو احمِ <اسم اللاعب>"
    if role.key == "engineer":
        return "📩 أرسل في الخاص: info"
    if role.key == "vendor":
        return "📩 أرسل في الخاص: message <اسم اللاعب>"
    if role.key == "bank":
        return "📩 أرسل في الخاص: bribe <اسم اللاعب>"
    return "❌ لا توجد قدرة متاحة لهذه الدور." 


def send_role_message(player: Player) -> None:
    role = RoleManager.get_role(player.role_key)
    caption = (
        f"🎭 <b>دورك السري:</b> {role.name}\n"
        f"{role.description}\n\n"
        f"{get_role_action_instructions(role)}\n"
        "أرسل الأمر في الخاص الآن لكي يحتسب." 
    )
    try:
        send_media(player.telegram_id, role.image_key, caption)
        player.role_message_sent = True
        player.private_connected = True
    except Exception:
        player.private_connected = False


def get_session_by_player_id(player_id: int):
    return session_manager.get_session_by_player_id(player_id)


def parse_target_identifier(text: str) -> str:
    words = text.strip().split()
    if not words:
        return ""
    if words[0].lower() in {"kill", "قتل", "save", "حمي", "check", "تحقق", "guard", "احمِ", "protect", "message", "رسالة", "bribe", "رشوة"}:
        return " ".join(words[1:]).strip()
    return text.strip()


def handle_private_action(session, player: Player, text: str) -> str:
    role = RoleManager.get_role(player.role_key)
    if not role.can_act_at_night:
        return "ليس لديك قدرة ليلية لهذه الليلة."
    target_string = parse_target_identifier(text)
    if role.key in {"godfather", "hitman", "deceiver", "impostor"}:
        if not target_string:
            return "اكتب: kill <اسم اللاعب> أو قتل <اسم اللاعب>"
        target = session.find_player_by_identifier(target_string)
        if not target:
            return f"لم أجد لاعباً باسم '{target_string}'. استخدم اسم المستخدم أو الاسم الأول أو رقم المعرف."
        if session.register_night_action(player.telegram_id, role.key, target.telegram_id):
            return f"✅ سجلت هدفك: {target.display_name()}"
        return "لم يتم تسجيل العملية. ربما استُخدمت القدرة أو الهدف غير صالح."
    if role.key == "doctor":
        if not target_string:
            return "اكتب: save <اسم اللاعب> أو حمي <اسم اللاعب>"
        target = session.find_player_by_identifier(target_string)
        if not target:
            return f"لم أجد لاعباً باسم '{target_string}'."
        if session.register_night_action(player.telegram_id, role.key, target.telegram_id):
            return f"✅ تم تسجيل حماية {target.display_name()} لهذه الليلة."
        return "لم يتم تسجيل الحماية. ربما اخترت نفس الهدف مرتين أو انتهت قدرتك."
    if role.key == "detective":
        if not target_string:
            return "اكتب: check <اسم اللاعب> أو تحقق <اسم اللاعب>"
        target = session.find_player_by_identifier(target_string)
        if not target:
            return f"لم أجد لاعباً باسم '{target_string}'."
        if session.register_night_action(player.telegram_id, role.key, target.telegram_id):
            return f"✅ تم تسجيل فحص {target.display_name()} هذه الليلة."
        return "لم يتم تسجيل الفحص. ربما انتهت قدرتك."
    if role.key == "bodyguard":
        if not target_string:
            return "اكتب: guard <اسم اللاعب> أو احمِ <اسم اللاعب>"
        target = session.find_player_by_identifier(target_string)
        if not target:
            return f"لم أجد لاعباً باسم '{target_string}'."
        if session.register_night_action(player.telegram_id, role.key, target.telegram_id):
            return f"✅ تم تسجيل الحماية لـ {target.display_name()} هذه الليلة."
        return "لم يتم تسجيل الحماية. ربما انتهت قدرتك."
    if role.key == "judge":
        if not target_string:
            return "اكتب: protect <اسم اللاعب> أو احمِ <اسم اللاعب>"
        target = session.find_player_by_identifier(target_string)
        if not target:
            return f"لم أجد لاعباً باسم '{target_string}'."
        if session.register_night_action(player.telegram_id, role.key, target.telegram_id):
            return f"✅ تم تسجيل حماية {target.display_name()} في التصويت القادم."
        return "لم يتم تسجيل الحماية. ربما انتهت قدرتك."
    if role.key == "engineer":
        if text.strip().lower() not in {"info", "معلومات", "status", "حالة"}:
            return "اكتب: info للحصول على تقرير المهندس."
        if session.register_night_action(player.telegram_id, role.key, player.telegram_id):
            return "✅ تم تسجيل دور المهندس. ستظهر لك نتيجة الفحص الليلة المقبلة."
        return "لم يتم تسجيل الدور. ربما انتهت قدرتك."
    if role.key == "vendor":
        if not target_string:
            return "اكتب: message <اسم اللاعب> أو رسالة <اسم اللاعب>"
        target = session.find_player_by_identifier(target_string)
        if not target:
            return f"لم أجد لاعباً باسم '{target_string}'."
        if session.register_night_action(player.telegram_id, role.key, target.telegram_id):
            return f"✅ تم تسجيل رسالة مجهولة لـ {target.display_name()} لهذه الليلة."
        return "لم يتم تسجيل الرسالة. ربما انتهت قدرتك."
    if role.key == "bank":
        if not target_string:
            return "اكتب: bribe <اسم اللاعب> أو رشوة <اسم اللاعب>"
        target = session.find_player_by_identifier(target_string)
        if not target:
            return f"لم أجد لاعباً باسم '{target_string}'."
        if session.register_night_action(player.telegram_id, role.key, target.telegram_id):
            return f"✅ تم تسجيل رشوة لـ {target.display_name()} إذا تم التصويت عليك."
        return "لم يتم تسجيل الرشوة. ربما انتهت قدرتك."
    return "هذه القدرة غير مدعومة حالياً."


@bot.message_handler(func=lambda message: message.chat.type == "private", content_types=["text"])
def private_message_handler(message):
    text = (message.text or "").strip()
    if not text:
        return
    session = get_session_by_player_id(message.from_user.id)
    if not session:
        return bot.reply_to(message, "لا توجد لعبة نشطة لك الآن.")
    if session.phase != "night":
        return bot.reply_to(message, "الآن ليس وقت الليل. يمكنك استخدام قدراتك فقط خلال الليل.")
    player = session.get_player(message.from_user.id)
    if not player or not player.alive:
        return bot.reply_to(message, "أنت خارج اللعبة أو لست حياً الآن.")
    response = handle_private_action(session, player, text)
    bot.reply_to(message, response)


def create_join_markup(chat_id: int):
    button = InlineKeyboardButton(text="🎮 انضم للعبة الآن", url=f"https://t.me/{get_bot_username()}?start=join_{chat_id}")
    markup = InlineKeyboardMarkup()
    markup.row(button)
    return markup


def owner_keyboard():
    buttons = [
        [InlineKeyboardButton(text="📋 الجلسات النشطة", callback_data="admin_sessions")],
        [InlineKeyboardButton(text="📊 إحصائيات البوت", callback_data="admin_stats")],
        [InlineKeyboardButton(text="📢 إرسال إعلان", callback_data="admin_broadcast")],
        [InlineKeyboardButton(text="🧹 تنظيف الجلسات", callback_data="admin_cleanup")],
    ]
    return build_inline_keyboard(buttons)


def get_mode_timers(mode: str):
    return SESSION_MODES.get(mode, SESSION_MODES["normal"])


def registration_timeout(chat_id: int, session):
    time.sleep(session.registration_time)
    with active_sessions_lock:
        if session.phase != "join":
            return
        if session.alive_count() < 4:
            bot.send_message(chat_id, "❌ تم إلغاء اللعبة لعدم اكتمال العدد (4 لاعبين على الأقل).")
            session_manager.remove_session(chat_id)
            logger.log_game(f"Session {chat_id} canceled by registration timeout.")
            return
        session.phase = "night"
        session.distribute_roles()
        for player in session.players.values():
            send_role_message(player)
        send_media(chat_id, "night", "⚙️ انتهى وقت التسجيل. تم توزيع الأدوار. بداية ليلة اللعب...")
        threading.Thread(target=run_night_cycle, args=(session,), daemon=True).start()


def run_night_cycle(session):
    while True:
        session.night_number += 1
        session.phase = "night"
        send_media(session.chat_id, "night", f"🌙 تبدأ الليلة رقم {session.night_number}. أرسلوا أفعالك في الخاص للبوت.")
        send_phase_countdown(session.chat_id, session.night_time, "وقت الليل")
        results = resolver.resolve_night(session)
        message_parts = results.get("kills", []) + results.get("investigations", []) + results.get("messages", [])
        send_media(session.chat_id, "day", f"☀️ انتهى الليل.\n{ '\n'.join(message_parts) if message_parts else 'لم يحدث شيء مهم الليلة.' }")
        session.phase = "voting"
        keyboard = build_inline_keyboard([
            [InlineKeyboardButton(text=player.display_name(), callback_data=f"vote_{session.chat_id}_{player.telegram_id}")]
            for player in session.get_alive_players()
        ])
        bot.send_message(session.chat_id, "🔊 الوقت مفتوح للتصويت. اختر اللاعب الذي تريد طرده:", reply_markup=keyboard)
        send_phase_countdown(session.chat_id, session.day_time, "وقت التصويت")
        result = session.process_voting()
        bot.send_message(session.chat_id, result)
        winner = session.check_game_over()
        if winner:
            announce_winner(session, winner)
            break


def announce_winner(session, winner: str):
    if winner == "city":
        text = "🏆 فازت المدينة!"
        image_key = "win_city_img"
    elif winner == "mafia":
        text = "💀 فازت المافيا!"
        image_key = "win_mafia_img"
    else:
        text = "🎭 فاز الجوكر!"
        image_key = "win_jester_img"
    send_media(session.chat_id, image_key, text)
    logger.log_game(f"Session {session.chat_id} ended with winner {winner}")
    for player in session.players.values():
        if winner == "mafia":
            _db_service.update_user_result(player.telegram_id, "win_mafia")
        elif winner == "city":
            _db_service.update_user_result(player.telegram_id, "win_city")
        elif winner == "jester":
            _db_service.update_user_result(player.telegram_id, "win_jester")
        else:
            _db_service.update_user_result(player.telegram_id, "loss")
    stats.record_game(session.mode, session.alive_count(), time.time() - session.created_at, winner)
    session.phase = "finished"
    session_manager.remove_session(session.chat_id)


@bot.message_handler(commands=["start"])
def command_start(message):
    text = message.text or ""
    _db_service.register_user(message.from_user.id, message.from_user.username or "", message.from_user.first_name or "")
    if text.startswith("/start join_"):
        try:
            chat_id = int(text.split("join_", 1)[1])
        except ValueError:
            return bot.reply_to(message, "رابط الانضمام غير صالح.")
        session = session_manager.get_session(chat_id)
        if not session or session.phase != "join":
            return bot.reply_to(message, "لا توجد لعبة مفتوحة للانضمام الآن.")
        if message.from_user.id in session.players:
            bot.reply_to(message, "أنت بالفعل مسجل في اللعبة.")
            return
        player = Player(
            telegram_id=message.from_user.id,
            username=message.from_user.username or "",
            first_name=message.from_user.first_name or "",
        )
        session.add_player(player)
        bot.reply_to(message, "✅ تم تسجيلك في اللعبة. انتظر بدء اللعبة.")
        bot.send_message(chat_id, f"👤 {player.display_name()} انضم إلى اللعبة.")
        return
    bot.reply_to(message, "مرحباً! استخدم /help لعرض الأوامر.")


@bot.message_handler(commands=["help"])
def command_help(message):
    bot.reply_to(message,
                 "📜 أوامر البوت:\n/mafia - بدء لعبة جديدة في المجموعة\n/status - حالة البوت\n/profile - ملفك الشخصي\n/admin - لوحة الإدارة إذا كنت مطوراً")


@bot.message_handler(commands=["mafia"])
def command_mafia(message):
    if message.chat.type == "private":
        return bot.reply_to(message, "هذا الأمر يعمل داخل المجموعات فقط.")
    chat_id = message.chat.id
    with active_sessions_lock:
        if session_manager.get_session(chat_id):
            return bot.reply_to(message, "هناك لعبة قائمة بالفعل في هذه المجموعة.")
        session = session_manager.create_session(chat_id, mode="normal")
        session.registration_time, session.night_time, session.day_time = get_mode_timers("normal")
        session.phase = "join"
        send_media(chat_id, "start", f"🎭 تم إنشاء لعبة جديدة! لديك {session.registration_time} ثانية للانضمام.", reply_markup=create_join_markup(chat_id))
        threading.Thread(target=registration_timeout, args=(chat_id, session), daemon=True).start()
        threading.Thread(target=send_phase_countdown, args=(chat_id, session.registration_time, "وقت التسجيل"), daemon=True).start()


@bot.message_handler(commands=["profile"])
def command_profile(message):
    profile = _db_service.get_profile(message.from_user.id)
    if not profile:
        return bot.reply_to(message, "لم يتم العثور على بيانات ملفك الشخصي بعد.")
    win_rate = 0.0
    if profile["games_played"]:
        win_rate = profile["wins"] / profile["games_played"] * 100
    bot.reply_to(message,
                 f"📌 ملفك الشخصي:\nعدد الألعاب: {profile['games_played']}\nالانتصارات: {profile['wins']}\nالهزائم: {profile['losses']}\nمعدل الفوز: {win_rate:.1f}%\nفوز الجوكر: {profile['jester_wins']}\nفوز المدينة: {profile['city_wins']}\nفوز المافيا: {profile['mafia_wins']}")


@bot.message_handler(commands=["status"])
def command_status(message):
    active = len(session_manager.active_sessions())
    stats_data = _db_service.get_stats()
    bot.reply_to(message,
                 f"🟢 Bot Status: Online\nActive Sessions: {active}\nUsers: {stats_data['total_users']}\nGames Recorded: {stats_data['total_games']}\nDatabase Size: {stats_data['database_size']} bytes")


@bot.message_handler(commands=["admin"])
def command_admin(message):
    if not is_owner(message.from_user.id, message.from_user.username):
        return bot.reply_to(message, "❌ لا تملك صلاحية الوصول إلى لوحة الإدارة.")
    bot.reply_to(message, "لوحة الإدارة الخاصة بك:", reply_markup=owner_keyboard())


@bot.callback_query_handler(func=lambda call: call.data and call.data.startswith("admin_"))
def callback_admin(call):
    if not is_owner(call.from_user.id, call.from_user.username):
        return bot.answer_callback_query(call.id, "ليس لديك صلاحية.")
    action = call.data.split("admin_", 1)[1]
    if action == "sessions":
        active = session_manager.active_sessions()
        rows = [f"{idx + 1}. Chat {s.chat_id}: {len(s.players)} لاعب، المرحلة {s.phase}, ليلة {s.night_number}" for idx, s in enumerate(active)]
        bot.answer_callback_query(call.id, "\n".join(rows) or "لا توجد جلسات حالياً.")
    elif action == "stats":
        summary = stats.summary()
        bot.answer_callback_query(call.id,
                                  f"ألعاب: {summary['games_played']}, متوسط المدة: {summary['average_duration']:.1f}s, إجمالي اللاعبين: {summary['total_players']}")
    elif action == "cleanup":
        count = 0
        for session in session_manager.active_sessions():
            if session.phase == "finished":
                session_manager.remove_session(session.chat_id)
                count += 1
        bot.answer_callback_query(call.id, f"تم تنظيف {count} جلسة منتهية.")
    else:
        bot.answer_callback_query(call.id, "الخيار قيد التطوير.")


@bot.callback_query_handler(func=lambda call: call.data and call.data.startswith("vote_"))
def callback_vote(call):
    parts = call.data.split("_")
    if len(parts) != 3:
        return
    chat_id = int(parts[1])
    target_id = int(parts[2])
    session = session_manager.get_session(chat_id)
    if not session or session.phase != "voting":
        return bot.answer_callback_query(call.id, "لا يمكن التصويت الآن.")
    if not session.vote(call.from_user.id, target_id):
        return bot.answer_callback_query(call.id, "التصويت غير صالح أو أنت ميت.")
    bot.answer_callback_query(call.id, "✅ تم تسجيل صوتك.")


if __name__ == "__main__":
    print("Starting Telegram bot polling...")
    try:
        bot.polling(non_stop=False, timeout=60, long_polling_timeout=60, logger_level=logging.ERROR)
    except ApiTelegramException as e:
        logger.log_game(f"Polling API exception: {e}")
        print("Telegram API polling conflict detected:", e)
        print("Make sure no other bot instance or webhook is active for this token.")
    except Exception as exc:
        logger.log_game(f"Polling exception: {exc}")
        print("Bot polling exception:", exc)
    else:
        print("Bot polling stopped. If this is due to a Telegram 409 conflict, stop the other bot instance or webhook.")
