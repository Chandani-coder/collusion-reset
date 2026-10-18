"""Branch isolation and a review-gated, communication-content control.

The live harness adapter must split task evidence from peer interaction. This
module cannot determine whether that semantic split is valid.
"""

from copy import deepcopy
from dataclasses import dataclass
from hashlib import sha256


CORE_CONDITIONS = ("continue", "reset_a", "reset_b", "reset_both")
EXPOSURE_CONDITION = "reset_b_neutral_peer_replay"


@dataclass
class Checkpoint:
    checkpoint_id: str
    history_a: list
    history_b: list
    task_state: dict


@dataclass
class Branch:
    condition: str
    state: Checkpoint


@dataclass(frozen=True)
class PeerMessage:
    task_evidence: str
    peer_interaction: str


def build_branches(checkpoint, include_exposure_control=True):
    """Reset once at a post-reflection boundary; later history can accumulate.

    Current rules/configuration belong outside historical lists. The live adapter
    must include all mutable environment state in task_state or isolate it itself.
    """
    conditions = CORE_CONDITIONS + (
        (EXPOSURE_CONDITION,) if include_exposure_control else ()
    )
    branches = {}
    for condition in conditions:
        state = deepcopy(checkpoint)
        if condition in ("reset_a", "reset_both"):
            state.history_a = []
        if condition in ("reset_b", "reset_both", EXPOSURE_CONDITION):
            state.history_b = []
        branches[condition] = Branch(condition, state)
    return branches


def _fingerprint(text):
    return sha256(text.encode("utf-8")).hexdigest()


def route_peer_message(
    condition,
    recipient,
    original,
    *,
    slot_id,
    neutral=None,
    review_reference=None,
    max_chars=200,
):
    """Return delivered structured content and an audit event.

    Only the survivor A -> newcomer B interaction segment changes in the extra
    arm. All arms are subject to the same supplied per-message character limit.
    A neutral message is a pre-reviewed, slot-matched fixture, not a live rewrite.
    No model calls, scoring labels or automatic content classification occur here.
    """
    if condition not in (*CORE_CONDITIONS, EXPOSURE_CONDITION):
        raise ValueError("Unknown condition")
    if recipient not in ("A", "B"):
        raise ValueError("Recipient must be A or B")
    if not slot_id or not isinstance(max_chars, int) or max_chars <= 0:
        raise ValueError("A slot ID and positive character limit are required")
    if not isinstance(original, PeerMessage):
        raise TypeError("Original message must be PeerMessage")
    delivered = original
    transformed = condition == EXPOSURE_CONDITION and recipient == "B"
    if transformed:
        if not review_reference or not isinstance(neutral, PeerMessage):
            raise ValueError("Exposure control requires a reviewed neutral fixture")
        if neutral.task_evidence != original.task_evidence:
            raise ValueError("Neutral replay must preserve task evidence exactly")
        delivered = neutral
    for message in (original, delivered):
        if len(message.task_evidence) + len(message.peer_interaction) > max_chars:
            raise ValueError("Message exceeds communication limit; no silent truncation")
    event = {
        "condition": condition,
        "recipient": recipient,
        "slot_id": slot_id,
        "transformed": transformed,
        "review_reference": review_reference if transformed else None,
        "evidence_sha256": _fingerprint(original.task_evidence),
        "original_interaction_sha256": _fingerprint(original.peer_interaction),
        "delivered_interaction_sha256": _fingerprint(delivered.peer_interaction),
        "original_chars": len(original.task_evidence) + len(original.peer_interaction),
        "delivered_chars": len(delivered.task_evidence) + len(delivered.peer_interaction),
    }
    return delivered, event
