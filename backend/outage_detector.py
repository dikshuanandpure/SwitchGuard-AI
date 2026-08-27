def calculate_outage_confidence(result):
    """
    Calculate confidence that failures represent
    a systemic outage rather than random or mixed failures.

    The score uses:
    - Failure rate
    - Transaction volume
    - Failed transaction volume
    - Error concentration
    - Small sample penalty
    """

    failure_rate = result["failure_rate"]
    total = result["total_transactions"]
    failed = result["failed_transactions"]
    error_concentration = result["error_concentration"]

    # 1. Failure rate score (maximum 30)
    failure_score = failure_rate * 30

    # 2. Transaction volume score (maximum 20)
    volume_score = min(total / 50, 1) * 20

    # 3. Failed transaction volume score (maximum 15)
    failed_score = min(failed / 30, 1) * 15

    # 4. Error concentration score (maximum 35)
    # Consistent failures are strong evidence
    # of a systemic issue.
    error_score = error_concentration * 35

    confidence = (
        failure_score
        + volume_score
        + failed_score
        + error_score
    )

    # Small sample penalty
    if total < 5:
        confidence *= 0.50

    elif total < 10:
        confidence *= 0.70

    return round(confidence, 2)


def get_outage_decision(confidence, result):
    """
    Convert confidence into an outage decision.

    Error concentration is used as a safety gate.
    High failure volume alone should not automatically
    mean a systemic outage.
    """

    error_concentration = result["error_concentration"]
    failed = result["failed_transactions"]

    # Too little evidence
    if failed < 5:
        return "INSUFFICIENT_EVIDENCE"

    # Many failures but different causes.
    # Do not classify this as one systemic outage.
    if error_concentration < 0.50:
        return "MIXED_FAILURE_PATTERN"

    if confidence >= 80:
        return "HIGH_CONFIDENCE_OUTAGE"

    elif confidence >= 55:
        return "POSSIBLE_OUTAGE_MONITOR"

    else:
        return "INSUFFICIENT_EVIDENCE"