import random
import threading
import time
from typing import Dict, Optional
from player import Player
from role_manager import RoleManager

class GameSession:
    PHASES = ("join", "night", "day", "voting", "finished")

    def __init__(self, chat_id: int, mode: str = "normal"):
        self.chat_id = chat_id
        self.mode = mode
        self.phase = "join"
        self.created_at = time.time()
        self.night_number = 0
        self.players: Dict[int, Player] = {}
        self.night_actions: Dict[int, dict] = {}
        self.votes: Dict[int, int] = {}
        self.voted_by: Dict[int, int] = {}
        self.session_lock = threading.RLock()
        self.judge_protect_target: Optional[int] = None
        self.last_detective_target: Optional[int] = None
        self.pending_timer: Optional[threading.Timer] = None

    def add_player(self, player: Player) -> bool:
        with self.session_lock:
            if player.telegram_id in self.players:
                return False
            self.players[player.telegram_id] = player
            return True

    def remove_player(self, telegram_id: int) -> bool:
        with self.session_lock:
            return self.players.pop(telegram_id, None) is not None

    def get_alive_players(self) -> list[Player]:
        return [player for player in self.players.values() if player.alive]

    def is_ready_to_start(self) -> bool:
        return len(self.players) >= 4

    def distribute_roles(self) -> None:
        with self.session_lock:
            player_count = len(self.players)
            roles = RoleManager.resolve_roles_for_player_count(player_count)
            random.shuffle(roles)
            players = list(self.players.values())
            random.shuffle(players)
            for player, role in zip(players, roles):
                player.role_key = role.key
                player.team = role.team
                player.uses[role.key] = -1 if role.max_uses == -1 else role.max_uses

    def get_player(self, telegram_id: int) -> Optional[Player]:
        return self.players.get(telegram_id)

    def alive_count(self) -> int:
        return len(self.get_alive_players())

    def vote(self, voter_id: int, target_id: int) -> bool:
        with self.session_lock:
            if voter_id not in self.players or target_id not in self.players:
                return False
            voter = self.players[voter_id]
            target = self.players[target_id]
            if not voter.alive or not target.alive or voter_id == target_id:
                return False
            previous = self.voted_by.get(voter_id)
            if previous is not None:
                self.votes[previous] -= 1
                if self.votes[previous] <= 0:
                    self.votes.pop(previous, None)
            self.votes[target_id] = self.votes.get(target_id, 0) + 1
            self.voted_by[voter_id] = target_id
            return True

    def register_night_action(self, actor_id: int, role_key: str, target_id: int) -> bool:
        with self.session_lock:
            actor = self.players.get(actor_id)
            if not actor or not actor.alive:
                return False
            if actor.role_key != role_key:
                return False
            if actor.used_skill and RoleManager.get_role(role_key).one_time:
                return False
            if target_id not in self.players or not self.players[target_id].alive:
                return False
            self.night_actions[actor_id] = {
                "role": role_key,
                "target_id": target_id,
            }
            return True

    def clear_night_actions(self) -> None:
        with self.session_lock:
            self.night_actions.clear()

    def process_voting(self) -> str:
        with self.session_lock:
            if not self.votes:
                return "لم يصوت أحد، لا يوجد طرد اليوم."
            highest = max(self.votes.values())
            candidates = [uid for uid, count in self.votes.items() if count == highest]
            if len(candidates) > 1:
                self.votes.clear()
                self.voted_by.clear()
                return "⚖️ تعادل في الأصوات، لم يتم إعدام أي لاعب."
            target_id = candidates[0]
            target = self.players[target_id]
            if target_id == self.judge_protect_target:
                self.judge_protect_target = None
                self.votes.clear()
                self.voted_by.clear()
                return f"⚖️ القاضي أنقذ {target.display_name()} من الإعدام اليوم."
            if target.role_key == "bank" and target.uses.get("bank", 0) != 0:
                bribe_target = self.night_actions.get(target_id, {}).get("target_id")
                if bribe_target and self.players.get(bribe_target) and self.players[bribe_target].alive:
                    target.uses["bank"] = 0
                    self.players[bribe_target].alive = False
                    self.votes.clear()
                    self.voted_by.clear()
                    return f"💰 المصرفي أنقذ نفسه ورشّح {self.players[bribe_target].display_name()} للإعدام بدلاً منه."
            target.alive = False
            name = target.display_name()
            self.votes.clear()
            self.voted_by.clear()
            return f"🔥 تم طرد {name} من المدينة."

    def check_game_over(self) -> Optional[str]:
        alive = self.get_alive_players()
        mafia = [p for p in alive if p.team == "mafia"]
        city = [p for p in alive if p.team == "city"]
        independents = [p for p in alive if p.team == "independent"]
        if not mafia:
            return "city"
        if len(mafia) >= len(city) + len(independents):
            return "mafia"
        return None

class SessionManager:
    def __init__(self):
        self.sessions: Dict[int, GameSession] = {}
        self.manager_lock = threading.RLock()

    def create_session(self, chat_id: int, mode: str = "normal") -> GameSession:
        with self.manager_lock:
            if chat_id in self.sessions:
                raise ValueError("Session already exists for this chat")
            session = GameSession(chat_id, mode)
            self.sessions[chat_id] = session
            return session

    def get_session(self, chat_id: int) -> Optional[GameSession]:
        return self.sessions.get(chat_id)

    def remove_session(self, chat_id: int) -> bool:
        with self.manager_lock:
            return self.sessions.pop(chat_id, None) is not None

    def active_sessions(self) -> list[GameSession]:
        return list(self.sessions.values())
