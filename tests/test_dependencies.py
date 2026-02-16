from tempfox import dependencies


def test_platform_info_returns_strings():
    system, arch = dependencies.get_platform_info()
    assert isinstance(system, str)
    assert isinstance(arch, str)
