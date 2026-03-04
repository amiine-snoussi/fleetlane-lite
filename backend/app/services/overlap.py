from datetime import datetime

def intervals_overlap(existing_start: datetime, existing_end: datetime, new_start: datetime, new_end: datetime) -> bool:
    """
    Conflict if:
      new_start < existing_end AND new_end > existing_start
    Touching edges are allowed (end == start is NOT overlap).
    """
    return new_start < existing_end and new_end > existing_start
