from dataclasses import dataclass
from typing import Optional

@dataclass
class Role:
    key: str
    name: str
    team: str
    description: str
    image_key: str
    can_act_at_night: bool = False
    one_time: bool = False
    max_uses: int = 1
    available_at_counts: Optional[list[int]] = None

class RoleManager:
    ROLES: dict[str, Role] = {
        "godfather": Role(
            key="godfather",
            name="Godfather",
            team="mafia",
            description="زعيم المافيا. يحدد ضحية الليل ويظهر بريئاً للمحقق.",
            image_key="godfather_img",
            can_act_at_night=True,
            one_time=False,
            max_uses=-1,
        ),
        "hitman": Role(
            key="hitman",
            name="Hitman",
            team="mafia",
            description="ينفذ القتل الليلي.",
            image_key="hitman_img",
            can_act_at_night=True,
            one_time=False,
            max_uses=-1,
        ),
        "deceiver": Role(
            key="deceiver",
            name="Deceiver",
            team="mafia",
            description="مرة واحدة: يجعل نفسه أو أحد المافيا يظهر بريئاً للمحقق.",
            image_key="deceiver_img",
            can_act_at_night=True,
            one_time=True,
        ),
        "impostor": Role(
            key="impostor",
            name="Impostor",
            team="mafia",
            description="مرة واحدة: يسرق دور لاعب ويحوّله إلى مواطن.",
            image_key="impostor_img",
            can_act_at_night=True,
            one_time=True,
        ),
        "detective": Role(
            key="detective",
            name="Detective",
            team="city",
            description="يكشف هوية لاعب كل ليلة.",
            image_key="detective_img",
            can_act_at_night=True,
            one_time=False,
            max_uses=-1,
        ),
        "doctor": Role(
            key="doctor",
            name="Doctor",
            team="city",
            description="يحمي لاعباً كل ليلة.",
            image_key="doctor_img",
            can_act_at_night=True,
            one_time=False,
            max_uses=-1,
        ),
        "bodyguard": Role(
            key="bodyguard",
            name="Bodyguard",
            team="city",
            description="يحمى لاعباً وإذا تعرض للهجوم يموت بدلاً منه.",
            image_key="bodyguard_img",
            can_act_at_night=True,
            one_time=False,
            max_uses=-1,
        ),
        "security": Role(
            key="security",
            name="Security Guard",
            team="city",
            description="مرة واحدة: يعيق لاعباً حتى نهاية اللعبة.",
            image_key="security_guard_img",
            can_act_at_night=True,
            one_time=True,
        ),
        "judge": Role(
            key="judge",
            name="Judge",
            team="city",
            description="مرة واحدة: يلغي نتيجة التصويت النهاري.",
            image_key="judge_img",
            can_act_at_night=True,
            one_time=True,
        ),
        "engineer": Role(
            key="engineer",
            name="Engineer",
            team="city",
            description="يعرف من تحققت معه نتائج المحقق الليلة السابقة.",
            image_key="engineer_img",
            can_act_at_night=True,
            one_time=False,
            max_uses=-1,
        ),
        "vendor": Role(
            key="vendor",
            name="Peddler",
            team="city",
            description="يرسل رسالة مجهولة للاعب آخر كل ليلة.",
            image_key="peddler_img",
            can_act_at_night=True,
            one_time=False,
            max_uses=-1,
        ),
        "bank": Role(
            key="bank",
            name="Banker",
            team="city",
            description="مرة واحدة: إذا تم التصويت عليه، يرسل لاعباً آخر إلى الإعدام بدلاً منه.",
            image_key="banker_img",
            can_act_at_night=True,
            one_time=True,
        ),
        "jester": Role(
            key="jester",
            name="Jester",
            team="independent",
            description="يفوز مباشرة إذا تم إعدامه بالتصويت.",
            image_key="jester_img",
            can_act_at_night=False,
            one_time=False,
        ),
        "traitor": Role(
            key="traitor",
            name="Traitor",
            team="independent",
            description="يتحول إلى المدينة إذا ماتت المافيا، وإلى المافيا إذا مات المدنيون.",
            image_key="traitor_img",
            can_act_at_night=False,
            one_time=False,
        ),
        "civilian": Role(
            key="civilian",
            name="Citizen",
            team="city",
            description="لا يملك قدرات خاصة.",
            image_key="citizen_img",
            can_act_at_night=False,
            one_time=False,
        ),
    }

    ROLE_DISTRIBUTIONS: dict[int, list[str]] = {
        4: ["godfather", "detective", "doctor", "civilian"],
        6: ["godfather", "hitman", "detective", "doctor", "civilian", "civilian"],
        8: ["godfather", "hitman", "detective", "doctor", "bodyguard", "civilian", "civilian", "civilian"],
        10: ["godfather", "hitman", "deceiver", "detective", "doctor", "bodyguard", "judge", "civilian", "civilian", "civilian"],
        12: ["godfather", "hitman", "deceiver", "detective", "doctor", "bodyguard", "judge", "engineer", "jester", "civilian", "civilian", "civilian"],
    }

    @classmethod
    def resolve_roles_for_player_count(cls, player_count: int) -> list[Role]:
        if player_count in cls.ROLE_DISTRIBUTIONS:
            keys = cls.ROLE_DISTRIBUTIONS[player_count].copy()
        else:
            keys = cls.ROLE_DISTRIBUTIONS[max(cls.ROLE_DISTRIBUTIONS.keys())].copy()
            keys += ["civilian"] * (player_count - max(cls.ROLE_DISTRIBUTIONS.keys()))
        return [cls.ROLES[key] for key in keys]

    @classmethod
    def get_role(cls, role_key: str) -> Role:
        return cls.ROLES.get(role_key, cls.ROLES["civilian"])

    @classmethod
    def night_order(cls) -> list[str]:
        return ["deceiver", "godfather", "hitman", "doctor", "bodyguard", "detective", "engineer", "vendor"]
