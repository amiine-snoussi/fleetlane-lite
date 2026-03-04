from datetime import datetime
from app.services.overlap import intervals_overlap

def dt(s: str) -> datetime:
    return datetime.fromisoformat(s)

def test_adjacent_is_not_overlap():
    assert intervals_overlap(dt("2026-03-04T10:00:00"), dt("2026-03-04T12:00:00"),
                             dt("2026-03-04T12:00:00"), dt("2026-03-04T13:00:00")) is False

def test_overlap_start_inside():
    assert intervals_overlap(dt("2026-03-04T10:00:00"), dt("2026-03-04T12:00:00"),
                             dt("2026-03-04T11:00:00"), dt("2026-03-04T13:00:00")) is True

def test_overlap_end_inside():
    assert intervals_overlap(dt("2026-03-04T10:00:00"), dt("2026-03-04T12:00:00"),
                             dt("2026-03-04T09:00:00"), dt("2026-03-04T11:00:00")) is True

def test_new_inside_existing():
    assert intervals_overlap(dt("2026-03-04T10:00:00"), dt("2026-03-04T14:00:00"),
                             dt("2026-03-04T11:00:00"), dt("2026-03-04T12:00:00")) is True

def test_new_covers_existing():
    assert intervals_overlap(dt("2026-03-04T10:00:00"), dt("2026-03-04T12:00:00"),
                             dt("2026-03-04T09:00:00"), dt("2026-03-04T13:00:00")) is True
