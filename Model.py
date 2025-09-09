import dataclasses
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

@dataclass
class Constraint:
    attribute: str          # AttributeId
    minCount: int

@dataclass
class AttributeStatistics:
    relativeFrequencies: Dict[str, float]  # { attributeId: 0.0~1.0 }
    correlations: Dict[str, Dict[str, float]]  # { attr1: {attr2: -1.0~1.0} }

@dataclass
class NewGameResponse:
    gameId: str
    constraints: List[Constraint]
    attributeStatistics: AttributeStatistics

    @staticmethod
    def from_json(j: dict) -> "NewGameResponse":
        constraints = [Constraint(**c) for c in j.get("constraints", [])]
        stats = j.get("attributeStatistics", {}) or {}
        rel = stats.get("relativeFrequencies", {}) or {}
        cor = stats.get("correlations", {}) or {}
        return NewGameResponse(
            gameId=j["gameId"],
            constraints=constraints,
            attributeStatistics=AttributeStatistics(rel, cor),
        )

@dataclass
class NextPerson:
    personIndex: int
    attributes: Dict[str, bool]  # { attributeId: boolean }

@dataclass
class DecideRunning:
    status: str                   # "running"
    admittedCount: int
    rejectedCount: int
    nextPerson: NextPerson

    @staticmethod
    def from_json(j: dict) -> "DecideRunning":
        p = j["nextPerson"]
        return DecideRunning(
            status=j["status"],
            admittedCount=j["admittedCount"],
            rejectedCount=j["rejectedCount"],
            nextPerson=NextPerson(
                personIndex=p["personIndex"],
                attributes=p["attributes"],
            ),
        )

@dataclass
class DecideCompleted:
    status: str                   # "completed"
    rejectedCount: int
    nextPerson: None

@dataclass
class DecideFailed:
    status: str                   # "failed"
    reason: str
    nextPerson: None