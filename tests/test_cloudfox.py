from tempfox import cloudfox


def test_check_token_expiration_matches_known_markers():
    assert cloudfox.check_token_expiration("ExpiredToken") is True
    assert cloudfox.check_token_expiration("no issues") is False
