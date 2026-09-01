import time
from typing import Dict

class StatisticsManager:
    def __init__(self):
        self.session_start = time.time()
        self.games_played = 0
        self.total_players = 0
        self.total_duration = 0.0
        self.win_counts: Dict[str, int] = {"mafia": 0, "city": 0, "jester": 0}

    def record_game(self, mode: str, players: int, duration: float, winner: str) -> None:
        self.games_played += 1
        self.total_players += players
        self.total_duration += duration
        if winner in self.win_counts:
            self.win_counts[winner] += 1

    def average_duration(self) -> float:
        if self.games_played == 0:
            return 0.0
        return self.total_duration / self.games_played

    def active_sessions(self, sessions: int) -> int:
        return sessions

    def summary(self) -> dict[str, object]:
        return {
            "games_played": self.games_played,
            "average_duration": self.average_duration(),
            "total_players": self.total_players,
            "win_counts": self.win_counts.copy(),
        }
