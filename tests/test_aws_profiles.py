from tempfox import aws_profiles


def test_generate_profile_name_includes_tempfox_prefix():
    name = aws_profiles.generate_profile_name("AKIA12345678ABCDEFG", "AKIA")
    assert name.startswith("tempfox-akia-")
