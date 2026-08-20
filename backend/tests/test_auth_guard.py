import pytest
from app.config import Settings


def test_dev_auth_guard_allows_dev_env():
    """Verify dev_bypass is allowed when ENV=dev."""
    s = Settings(ENV="dev", AUTH_MODE="dev_bypass")
    # Should not raise
    s.validate_dev_auth_guard()


def test_dev_auth_guard_blocks_non_dev_env():
    """Assert section 5 guard raises RuntimeError when AUTH_MODE=dev_bypass and ENV!=dev."""
    s = Settings(ENV="prod", AUTH_MODE="dev_bypass")
    with pytest.raises(RuntimeError) as exc_info:
        s.validate_dev_auth_guard()
    assert "CRITICAL SECURITY FAILURE" in str(exc_info.value)


def test_dev_auth_guard_allows_entra_jwt_in_prod():
    """Verify entra_jwt is allowed in prod."""
    s = Settings(ENV="prod", AUTH_MODE="entra_jwt")
    s.validate_dev_auth_guard()
