from dataclasses import dataclass, field
from typing import Dict, Optional

@dataclass
class Player:
    telegram_id: int
    username: str
    first_name: str
    role_key: str = "civilian"
    team: str = "city"
    alive: bool = True
    muted: bool = False
    protected: bool = False
    used_skill: bool = False
    last_protected_by: int | None = None
    uses: Dict[str, int] = field(default_factory=dict)
    joined_at: float = 0.0
    private_connected: bool = False
    role_message_sent: bool = False

    def display_name(self) -> str:
        return self.first_name or self.username or str(self.telegram_id)

    def can_act(self) -> bool:
        return self.alive and not self.muted and self.role_key != "civilian"

    def is_active(self) -> bool:
        return self.alive and not self.muted

    def use_skill(self, role_key: str) -> bool:
        max_uses = self.uses.get(role_key, 1)
        if max_uses == 0:
            return False
        if max_uses > 0:
            self.uses[role_key] = max_uses - 1
        return True

    def set_role(self, role_key: str, team: str):
        self.role_key = role_key
        self.team = team

    def is_restricted(self) -> bool:
        return not self.alive or self.muted
