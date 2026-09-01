# 🎭 Mafia Bot | لعبة المافيا

> **Interactive Mafia Game Bot for Telegram Groups**  
> **بوت لعبة المافيا التفاعلية لمجموعات تيليجرام**

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Active%20Development-brightgreen)]()

---

<div dir="ltr">

## 🌟 Features

- 🎮 **Full Mafia Game** - Complete game implementation with multiple roles
- 👥 **Multiplayer Support** - Play with 4-20 players in groups
- 🎭 **Multiple Roles** - Mafia, Doctor, Detective, Villagers, etc.
- 🌙 **Day/Night Cycles** - Realistic game flow
- 📊 **Game Statistics** - Track player stats and achievements
- 🎨 **Beautiful UI** - Interactive inline buttons and keyboards
- 🗣️ **Russian/Arabic Support** - Multi-language support

---

## 🛠️ Requirements

- Python 3.8+
- Telegram Bot Token
- SQLite Database

### Dependencies
```
pyTelegramBotAPI >= 4.0
requests >= 2.28.0
```

---

## 📦 Installation

```bash
git clone https://github.com/your-username/mafia-bot.git
cd mafia-bot

python -m venv venv
venv\Scripts\activate

pip install -r requirements.txt

cp .env.example .env
# Set your BOT_TOKEN and GROUP_ID
```

---

## 🚀 Usage

```bash
python bot.py
```

---

## 🎮 How to Play

1. **Create a game**: `/newgame` in a group
2. **Join the game**: Click "Присоединиться" button
3. **Start the game**: `/start` when enough players joined
4. **Night phase**: Mafia chooses victim
5. **Day phase**: Players vote to eliminate someone
6. **Continue**: Until Mafia or Villagers win

---

## 🎭 Roles

- **🔪 Mafia** - Eliminate villagers at night
- **🏥 Doctor** - Protect one player per night
- **🔍 Detective** - Check player role each night
- **👨‍🌾 Villagers** - Vote during day phase

---

## 📊 Project Structure

```
mafia_bot/
├── bot.py                  # Main bot file
├── config.py              # Configuration
├── game_logic.py          # Game mechanics
├── player.py              # Player class
├── role_manager.py        # Role assignment
├── session_manager.py     # Game sessions
├── action_resolver.py     # Action handling
├── models/                # Data models
├── handlers/              # Command handlers
├── services/              # Business logic
├── database.py            # Database operations
├── requirements.txt
└── README.md
```

---

## 🎮 Commands

| Command | Description |
|---------|-------------|
| `/newgame` | Start a new game |
| `/start` | Begin the game |
| `/cancel` | Cancel game |
| `/status` | Game status |
| `/players` | List players |
| `/help` | Help menu |
| `/stats` | Your statistics |

---

## 📝 License

MIT License

</div>

---

<div dir="rtl">

## 🌟 الميزات

- 🎮 **لعبة مافيا كاملة** - تطبيق شامل للعبة بأدوار متعددة
- 👥 **دعم متعدد اللاعبين** - لعب مع 4-20 لاعب في المجموعات
- 🎭 **أدوار متعددة** - مافيا، دكتور، محقق، قرويون، إلخ
- 🌙 **دورات الليل والنهار** - تدفق لعبة واقعي
- 📊 **إحصائيات اللعبة** - تتبع إحصائيات اللاعبين والإنجازات
- 🎨 **واجهة جميلة** - أزرار تفاعلية وألوحة مفاتيح
- 🗣️ **دعم اللغات** - دعم متعدد اللغات

---

## 🛠️ المتطلبات

- Python 3.8+
- Telegram Bot Token
- SQLite Database

### المكتبات المطلوبة
```
pyTelegramBotAPI >= 4.0
requests >= 2.28.0
```

---

## 📦 التثبيت

```bash
git clone https://github.com/your-username/mafia-bot.git
cd mafia-bot

python -m venv venv
venv\Scripts\activate

pip install -r requirements.txt

cp .env.example .env
# اضبط BOT_TOKEN و GROUP_ID
```

---

## 🚀 الاستخدام

```bash
python bot.py
```

---

## 🎮 كيفية اللعب

1. **إنشاء لعبة**: `/newgame` في المجموعة
2. **الانضمام**: انقر على زر "الانضمام"
3. **بدء اللعبة**: `/start` عند وجود لاعبين كافيين
4. **مرحلة الليل**: المافيا تختار الضحية
5. **مرحلة النهار**: اللاعبون يصوتون للتخلص من أحدهم
6. **المتابعة**: حتى تفوز المافيا أو القرويون

---

## 🎭 الأدوار

- **🔪 المافيا** - القضاء على القرويين في الليل
- **🏥 الدكتور** - حماية لاعب واحد كل ليلة
- **🔍 المحقق** - فحص دور اللاعب كل ليلة
- **👨‍🌾 القرويون** - التصويت خلال مرحلة النهار

---

## 🗂️ هيكل المشروع

```
mafia_bot/
├── bot.py                  # ملف البوت الرئيسي
├── config.py              # الإعدادات
├── game_logic.py          # آليات اللعبة
├── player.py              # فئة اللاعب
├── role_manager.py        # إدارة الأدوار
├── session_manager.py     # إدارة جلسات اللعبة
├── action_resolver.py     # معالجة الإجراءات
├── models/                # نماذج البيانات
├── handlers/              # معالجات الأوامر
├── services/              # منطق العمل
├── database.py            # عمليات قاعدة البيانات
├── requirements.txt
└── README.md
```

---

## 🎮 الأوامر

| الأمر | الوصف |
|------|-------|
| `/newgame` | بدء لعبة جديدة |
| `/start` | ابدأ اللعبة |
| `/cancel` | إلغاء اللعبة |
| `/status` | حالة اللعبة |
| `/players` | قائمة اللاعبين |
| `/help` | قائمة المساعدة |
| `/stats` | إحصائياتك |

---

## 📝 الترخيص

MIT License

</div>

---

**Last Updated**: 2026-09-01
