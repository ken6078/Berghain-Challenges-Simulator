# pip install requests
from __future__ import annotations
import requests
from typing import Optional, Union

# 這裡假設 Model.py 與此檔同資料夾
from Model import (
    NewGameResponse, DecideRunning, DecideCompleted, DecideFailed
)

DecideResult = Union[DecideRunning, DecideCompleted, DecideFailed]


class GameSession:
    """
    Encapsulate /new-game and /decide-and-next:
    - On initialization, automatically start a new game and store gameId and personIndex = 0.
    - Call next_person() to get the first person (personIndex = 0), no need to accept.
    - Subsequent calls to next_person(accept=True/False) will increment personIndex and return the parsed result.
    """
    def __init__(self, scenario: int, player_id: str, timeout: float = 15.0,):
        self.player_id = player_id
        self.base_url = "https://berghain.challenges.listenlabs.ai/"
        self.timeout = timeout
        self.session = requests.Session()

        self.new_game_resp = self._new_game(scenario, self.player_id)
        self.game_id = self.new_game_resp.gameId
        self.person_index = 0

    def _new_game(self, scenario: int, player_id: str) -> NewGameResponse:
        url = f"{self.base_url}/new-game"
        params = {"scenario": scenario, "playerId": player_id}
        resp = self.session.get(url, params=params, timeout=self.timeout)
        self._raise(resp)
        return NewGameResponse.from_json(resp.json())

    def _decide_and_next(self, accept: bool) -> DecideResult:
        url = f"{self.base_url}/decide-and-next"
        params = {
            "gameId": self.game_id,
            "personIndex": self.person_index,
            "accept" : str(accept).lower(),
        }

        resp = self.session.get(url, params=params, timeout=self.timeout)
        self._raise(resp)
        data = resp.json()
        status = data.get("status")

        if status == "running":
            parsed = DecideRunning.from_json(data)
            self.person_index = parsed.nextPerson.personIndex
            return parsed
        elif status == "completed":
            return DecideCompleted(status="completed",
                                   rejectedCount=data["rejectedCount"],
                                   nextPerson=None)
        elif status == "failed":
            return DecideFailed(status="failed",
                                reason=data.get("reason", "Unknown"),
                                nextPerson=None)
        else:
            raise ValueError(f"Unexpected status: {status!r}")

    def next_person(self, accept: Optional[bool] = None) -> DecideResult:
        return self._decide_and_next(accept)

    def get_first_person(self) -> DecideResult:
        url = f"{self.base_url}/decide-and-next"
        params = {
            "gameId": self.game_id,
            "personIndex": 0,
        }
        resp = self.session.get(url, params=params, timeout=self.timeout)
        self._raise(resp)
        data = resp.json()
        parsed = DecideRunning.from_json(data)
        return parsed


    @staticmethod
    def _raise(resp: requests.Response) -> None:
        try:
            resp.raise_for_status()
        except requests.HTTPError as e:
            try:
                body = resp.json()
            except Exception:
                body = resp.text[:500]
            raise requests.HTTPError(f"{e} | body={body}") from e