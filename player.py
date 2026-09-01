import time
from dataclasses import dataclass, field
from typing import Dict

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
    joined_at: float = field(default_factory=time.time)
    private_connected: bool = False
    role_message_sent: bool = False

    def display_name(self) -> str:
        return self.first_name or self.username or str(self.telegram_id)

    def can_act(self) -> bool:
        return self.alive and not self.muted and self.role_key != "civilian"

    def has_skill_available(self) -> bool:
        if self.role_key not in self.uses:
            return True
        value = self.uses[self.role_key]
        return value != 0

    @property
    def role(self) -> str:
        return self.role_key

    @property
    def display_role(self) -> str:
        return self.role_key.replace("_", " ").title()

    def use_skill(self) -> bool:
        if self.role_key not in self.uses:
            self.used_skill = True
            return True
        remaining = self.uses[self.role_key]
        if remaining == 0:
            return False
        if remaining > 0:
            self.uses[self.role_key] = remaining - 1
        self.used_skill = True
        return True
