
import json, uuid, math, os, random, pickle
from typing import Dict, Optional, List
import os
import numpy as np

from Model import (
    NewGameResponse, DecideRunning, DecideCompleted, DecideFailed,
)

class Simulator:
    VENUE_CAPACITY = 1000
    REJECT_LIMIT = 20000

    def __init__(self, problem_path: str):
        self.people_list = []
        self.problem_path = problem_path
        self.scenario_files = {
            1: os.path.join(problem_path, "p1.json"),
            2: os.path.join(problem_path, "p2.json"),
            3: os.path.join(problem_path, "p3.json")
        }
        self._games: Dict[str, dict] = {}

    # ----------------------- Public API -----------------------
    def new_game(self, scenario: int, player_id: str = "") -> NewGameResponse:
        with open(self.scenario_files[scenario], "r", encoding="utf-8") as f:
            j = json.load(f)

        folder_path = os.path.join(self.problem_path, "Dataset", f"p{scenario}")
        pkg_files = [f for f in os.listdir(folder_path) if f.endswith(".pkg")]
        chosen_pkg = random.choice(pkg_files)
        chosen_path = os.path.join(folder_path, chosen_pkg)
        with open(chosen_path, 'rb') as f:
            people_list = pickle.load(f)

        game_id = str(uuid.uuid4())
        j["gameId"] = game_id
        ngr = NewGameResponse.from_json(j)
        attrs = list(ngr.attributeStatistics.relativeFrequencies.keys())

        state = {
            "playerId": player_id,
            "gameId": game_id,
            "scenario": scenario,
            "attrs": attrs,
            "admitted": 0,
            "rejected": 0,
            "admitted_people": [],
            "last_person": None,
            "person_index": 0,
            "people_list": people_list
        }
        self._games[game_id] = state

        # Pre-sample first person
        state["last_person"] = self._random_people(state)

        return NewGameResponse(
            gameId=game_id,
            constraints=ngr.constraints,
            attributeStatistics=ngr.attributeStatistics,
        )

    def decide_and_next(self, game_id: str, accept: Optional[bool] = None):
        if game_id not in self._games:
            return DecideFailed(status="failed", reason="Unknown gameId", nextPerson=None)
        st = self._games[game_id]

        if accept is not None:
            if st["last_person"] is None:
                return DecideFailed(status="failed", reason="No pending person to decide", nextPerson=None)
            if accept:
                st["admitted"] += 1
                st["admitted_people"].append(st["last_person"])
            else:
                st["rejected"] += 1

            # Terminal checks
            if st["admitted"] >= self.VENUE_CAPACITY:
                # Check constraints at end
                with open(self.scenario_files[st["scenario"]], "r", encoding="utf-8") as f:
                    j = json.load(f)
                constraints = j["constraints"]
                counts = {a: 0 for a in st["attrs"]}
                for person in st["admitted_people"]:
                    for a, v in person.nextPerson.attributes.items():
                        if v:
                            counts[a] += 1
                for c in constraints:
                    if counts.get(c["attribute"], 0) < c["minCount"]:
                        return DecideFailed(status="failed", reason=f"constraints_not_satisfied:{c['attribute']}", nextPerson=None)
                return DecideCompleted(status="completed", rejectedCount=st["rejected"], nextPerson=None)
            if st["rejected"] >= self.REJECT_LIMIT:
                return DecideFailed(status="failed", reason="Rejected limit reached", nextPerson=None)

        last_person = self._random_people(st)
        last_person.admittedCount = st["admitted"]
        last_person.rejectedCount = st["rejected"]
        st["last_person"] = last_person
        return st["last_person"]

    def _random_people(self, state):
        return random.choice(state['people_list'])

    def settle_game(self, game_id: str) -> dict:
        """
        return type
        {
            "gameId": str,
            "status": "success" | "fail",
            "rejectedCount": int,
            "admittedCount": int,
            "constraints": [
                { "attribute": str, "required": int, "actual": int, "ok": bool }
            ]
        }
        """
        st = self._games.get(game_id)
        if st is None:
            return {
                "gameId": game_id,
                "status": "fail",
                "rejectedCount": 0,
                "admittedCount": 0,
                "constraints": [],
            }

        with open(self.scenario_files[st["scenario"]], "r", encoding="utf-8") as f:
            j = json.load(f)
        constraints = j.get("constraints", []) or []

        admitted_attr_counts = {a: 0 for a in st["attrs"]}
        for person in st.get("admitted_people", []) or []:
            for a, val in person.nextPerson.attributes.items():
                if val:
                    admitted_attr_counts[a] = admitted_attr_counts.get(a, 0) + 1

        results = []
        all_ok = True
        for c in constraints:
            attr = c["attribute"]
            required = int(c["minCount"])
            actual = int(admitted_attr_counts.get(attr, 0))
            ok = actual >= required
            results.append({
                "attribute": attr,
                "required": required,
                "actual": actual,
                "ok": ok,
            })
            if not ok:
                all_ok = False

        return {
            "gameId": game_id,
            "status": "success" if all_ok else "fail",
            "rejectedCount": int(st["rejected"]),
            "admittedCount": int(st["admitted"]),
            "constraints": results,
        }