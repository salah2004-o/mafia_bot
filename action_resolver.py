from typing import Dict, Optional

class ActionResolver:
    NIGHT_ORDER = ["deceiver", "godfather", "hitman", "doctor", "bodyguard", "detective", "engineer", "vendor"]

    def __init__(self):
        pass

    def resolve_night(self, session) -> Dict[str, str]:
        results = {
            "kills": [],
            "investigations": [],
            "messages": [],
        }

        night_actions = session.night_actions.copy()

        # Trickster / Impostor: steal role before the rest of the night
        for actor_id, action in night_actions.items():
            if action["role"] == "impostor" and action["target_id"]:
                results["messages"].append(self._resolve_impostor(session, actor_id, action["target_id"]))
            if action["role"] == "deceiver" and action["target_id"]:
                results["messages"].append(self._resolve_deceiver(session, actor_id, action["target_id"]))

        mafia_target_id = self._collect_mafia_target(session)
        doctor_target_id = self._last_action_target(session, "doctor")
        bodyguard_target_id = self._last_action_target(session, "bodyguard")
        detective_target_id = self._last_action_target(session, "detective")
        engineer_target_id = self._last_action_target(session, "engineer")
        vendor_target_id = self._last_action_target(session, "vendor")

        if detective_target_id:
            results["investigations"].append(self._resolve_detective(session, detective_target_id))

        if engineer_target_id:
            results["messages"].append(self._resolve_engineer(session, engineer_target_id))

        if vendor_target_id:
            results["messages"].append(self._resolve_vendor(session, vendor_target_id))

        killed = self._resolve_kill(session, mafia_target_id, doctor_target_id, bodyguard_target_id)
        if killed:
            results["kills"].append(killed)

        session.night_actions.clear()
        return results

    def _collect_mafia_target(self, session) -> Optional[int]:
        votes = {}
        for actor_id, action in session.night_actions.items():
            if action["role"] in {"godfather", "hitman", "deceiver", "impostor"}:
                target_id = action.get("target_id")
                if target_id and session.players[target_id].alive:
                    votes[target_id] = votes.get(target_id, 0) + 1
        if not votes:
            return None
        return max(votes, key=votes.get)

    def _last_action_target(self, session, role_name: str) -> Optional[int]:
        selected = [action["target_id"] for action in session.night_actions.values() if action["role"] == role_name and action.get("target_id")]
        return selected[-1] if selected else None

    def _resolve_detective(self, session, target_id: int) -> str:
        player = session.players[target_id]
        if player.team == "mafia":
            return f"تحقيق المحقق: اللاعب {player.display_name()} يبدو مافيا."
        if player.team == "independent":
            return f"تحقيق المحقق: اللاعب {player.display_name()} مستقل ولا ينتمي للمدينة."
        return f"تحقيق المحقق: اللاعب {player.display_name()} يظهر كمدني."

    def _resolve_engineer(self, session, target_id: int) -> str:
        if session.last_detective_target and session.players.get(session.last_detective_target):
            return f"المهندس وجد أن المحقق حقق مع {session.players[session.last_detective_target].display_name()} الليلة الماضية."
        return "المهندس لم يجد نتيجة مفيدة هذه الليلة."

    def _resolve_vendor(self, session, target_id: int) -> str:
        player = session.players[target_id]
        return f"رسالة مجهولة وصلت إلى {player.display_name()} الليلة الماضية." if player else "لم يتم إرسال رسالة مجهولة هذه الليلة."

    def _resolve_deceiver(self, session, actor_id: int, target_id: int) -> str:
        if target_id not in session.players or not session.players[target_id].alive:
            return "لم يتم تنفيذ خدعة الماكر هذه الليلة."
        return f"خدعة التزييف: {session.players[target_id].display_name()} سيظهر بريئًا للمحقق هذه الليلة."

    def _resolve_impostor(self, session, actor_id: int, target_id: int) -> str:
        if target_id not in session.players or not session.players[target_id].alive:
            return "لم يتم تنفيذ سرقة الدور هذه الليلة."
        victim = session.players[target_id]
        actor = session.players[actor_id]
        stolen_role = victim.role_key
        stolen_team = victim.team
        victim.role_key = "civilian"
        victim.team = "city"
        actor.role_key = stolen_role
        actor.team = stolen_team
        return f"المحتال سرق دور {victim.display_name()} وأصبح الأخير مواطنًا."

    def _resolve_kill(self, session, mafia_target_id: Optional[int], doctor_target_id: Optional[int], bodyguard_target_id: Optional[int]) -> Optional[str]:
        if not mafia_target_id:
            return None
        if doctor_target_id == mafia_target_id:
            return None
        if bodyguard_target_id == mafia_target_id:
            guard = next((p for p in session.players.values() if p.role_key == "bodyguard" and p.alive), None)
            if guard:
                guard.alive = False
                return f"الحارس ضحى بنفسه لحماية الهدف، فمات {guard.display_name()}."
        victim = session.players[mafia_target_id]
        victim.alive = False
        return f"المافيا قتلت {victim.display_name()} هذه الليلة."
