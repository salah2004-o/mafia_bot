from dataclasses import dataclass
from typing import ClassVar, List, Dict, Optional

@dataclass
class Role:
    name: str
    team: str
    description: str
    image_key: str
    can_act_at_night: bool = False
    one_time: bool = False
    max_uses: int = 1
    available_in_counts: Optional[List[int]] = None

class RoleManager:
    ROLE_TABLE: ClassVar[Dict[str, Role]] = {
        "godfather": Role(
            name="Godfather",
            team="mafia",
            description="زعيم المافيا. يحدد الضحية الليلي ويظهر بريئًا للمحقق.",
            image_key="godfather_img",
            can_act_at_night=True,
            one_time=False,
            max_uses=-1,
        ),
        "hitman": Role(
            name="Hitman",
            team="mafia",
            description="ينفذ القتل الليلي بناءً على قرار المافيا.",
            image_key="hitman_img",
            can_act_at_night=True,
            one_time=False,
            max_uses=-1,
        ),
        "deceiver": Role(
            name="Deceiver",
            team="mafia",
            description="مرة واحدة: يجعل نفسه أو عضوًا من المافيا يظهر بريئًا للمحقق.",
            image_key="deceiver_img",
            can_act_at_night=True,
            one_time=True,
        ),
        "impostor": Role(
            name="Impostor",
            team="mafia",
            description="مرة واحدة: يسرق دور لاعب لتحويله لمواطن.",
            image_key="impostor_img",
            can_act_at_night=True,
            one_time=True,
        ),
        "detective": Role(
            name="Detective",
            team="city",
            description="يكشف هوية لاعب ليعرف إن كان مافيا أو مدني أو مستقل.",
            image_key="detective_img",
            can_act_at_night=True,
            one_time=False,
            max_uses=-1,
        ),
        "doctor": Role(
            name="Doctor",
            team="city",
            description="يحمي لاعبًا كل ليلة ولا يمكنه حماية نفس الشخص مرتين متتالية.",
            image_key="doctor_img",
            can_act_at_night=True,
            one_time=False,
            max_uses=-1,
        ),
        "bodyguard": Role(
            name="Bodyguard",
            team="city",
            description="يحمي لاعبًا. إذا هوجم، يموت الحارس بدلًا منه.",
            image_key="bodyguard_img",
            can_act_at_night=True,
            one_time=False,
            max_uses=-1,
        ),
        "security": Role(
            name="Security Guard",
            team="city",
            description="مرة واحدة: يعطل لاعبًا حتى نهاية اللعبة. يفقد حق التصويت والكلام.",
            image_key="security_guard_img",
            can_act_at_night=True,
            one_time=True,
        ),
        "judge": Role(
            name="Judge",
            team="city",
            description="مرة واحدة: يلغي نتيجة تصويت نهاري.",
            image_key="judge_img",
            can_act_at_night=True,
            one_time=True,
        ),
        "engineer": Role(
            name="Engineer",
            team="city",
            description="يعرف من حقق معه المحقق في الليلة الماضية.",
            image_key="engineer_img",
            can_act_at_night=True,
            one_time=False,
            max_uses=-1,
        ),
        "vendor": Role(
            name="Peddler",
            team="city",
            description="يرسل رسالة مجهولة للاعب آخر كل ليلة.",
            image_key="peddler_img",
            can_act_at_night=True,
            one_time=False,
            max_uses=-1,
        ),
        "bank": Role(
            name="Banker",
            team="city",
            description="مرة واحدة: إذا تم التصويت عليه، يختار لاعباً آخر ليموت بدلاً منه.",
            image_key="banker_img",
            can_act_at_night=True,
            one_time=True,
        ),
        "jester": Role(
            name="Jester",
            team="independent",
            description="يفوز مباشرة إذا تم إعدامه بالتصويت.",
            image_key="jester_img",
            can_act_at_night=False,
            one_time=False,
        ),
        "traitor": Role(
            name="Traitor",
            team="independent",
            description="ينضم للمدينة إذا ماتت المافيا، وينضم للمافيا إذا مات المدنيون.",
            image_key="traitor_img",
            can_act_at_night=False,
            one_time=False,
        ),
        "civilian": Role(
            name="Citizen",
            team="city",
            description="لا يملك قدرات خاصة ولكنه جزء من المدينة.",
            image_key="citizen_img",
            can_act_at_night=False,
            one_time=False,
        ),
    }

    ROLE_DISTRIBUTION: ClassVar[Dict[int, List[str]]] = {
        4: ["godfather", "detective", "doctor", "civilian"],
        6: ["godfather", "hitman", "detective", "doctor", "civilian", "civilian"],
        8: ["godfather", "hitman", "detective", "doctor", "bodyguard", "civilian", "civilian", "civilian"],
        10: ["godfather", "hitman", "deceiver", "detective", "doctor", "bodyguard", "judge", "civilian", "civilian", "civilian"],
        12: ["godfather", "hitman", "deceiver", "detective", "doctor", "bodyguard", "judge", "engineer", "jester", "civilian", "civilian", "civilian"],
    }

    @classmethod
    def get_roles_for_count(cls, count: int) -> List[Role]:
        if count in cls.ROLE_DISTRIBUTION:
            role_keys = cls.ROLE_DISTRIBUTION[count].copy()
        else:
            role_keys = cls.ROLE_DISTRIBUTION[max(cls.ROLE_DISTRIBUTION.keys())].copy()
            extra = count - max(cls.ROLE_DISTRIBUTION.keys())
            role_keys += ["civilian"] * extra

        assigned_roles = []
        for role_key in role_keys:
            assigned_roles.append(cls.ROLE_TABLE.get(role_key, cls.ROLE_TABLE["civilian"]))
        return assigned_roles

    @classmethod
    def get_role(cls, role_key: str) -> Role:
        return cls.ROLE_TABLE.get(role_key, cls.ROLE_TABLE["civilian"])

    @classmethod
    def get_night_order(cls) -> List[str]:
        return ["deceiver", "godfather", "hitman", "doctor", "bodyguard", "detective", "engineer", "vendor"]
