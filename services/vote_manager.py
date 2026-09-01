from typing import Dict, Optional

class VoteManager:
    def __init__(self):
        self.votes: Dict[int, int] = {}
        self.voted_by: Dict[int, int] = {}

    def cast_vote(self, voter_id: int, target_id: int, players: Dict[int, object]) -> bool:
        if voter_id not in players or target_id not in players:
            return False
        voter = players[voter_id]
        target = players[target_id]
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

    def reset(self) -> None:
        self.votes.clear()
        self.voted_by.clear()

    def results(self) -> tuple[Optional[int], list[int]]:
        if not self.votes:
            return None, []
        highest = max(self.votes.values())
        candidates = [uid for uid, count in self.votes.items() if count == highest]
        return highest, candidates

    def has_votes(self) -> bool:
        return bool(self.votes)
