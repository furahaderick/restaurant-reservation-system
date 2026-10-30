from datetime import datetime, timedelta, timezone

import pytest

from restaurant_app.reservations import validate_booking


def test_valid_booking_times_are_accepted():
    starts_at = datetime.now(timezone.utc)
    ends_at = starts_at + timedelta(hours=2)
    validate_booking(starts_at, ends_at, 4)


@pytest.mark.parametrize("party_size", [0, -1, 1.5])
def test_invalid_party_size_is_rejected(party_size):
    starts_at = datetime.now(timezone.utc)
    ends_at = starts_at + timedelta(hours=2)
    with pytest.raises(ValueError):
        validate_booking(starts_at, ends_at, party_size)


def test_end_must_be_after_start():
    starts_at = datetime.now(timezone.utc)
    with pytest.raises(ValueError):
        validate_booking(starts_at, starts_at, 2)


def test_timezone_is_required():
    starts_at = datetime(2026, 11, 1, 18, 0)
    ends_at = datetime(2026, 11, 1, 20, 0)
    with pytest.raises(ValueError):
        validate_booking(starts_at, ends_at, 2)
