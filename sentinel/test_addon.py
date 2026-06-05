"""
Phase 219 tests — SENTINEL HA Add-on
"""
import pytest
from entity_discovery import validate_entity_id


class TestEntityValidation:
    def test_valid_entity_id(self):
        assert validate_entity_id("sensor.battery_soc") is True
        assert validate_entity_id("sensor.pv_power_w") is True

    def test_invalid_entity_id(self):
        assert validate_entity_id("") is False
        assert validate_entity_id("sensor/../../../etc") is False  # path traversal
        assert validate_entity_id("sensor*") is False  # wildcard

    def test_max_length(self):
        long_id = "sensor." + "a" * 100
        assert validate_entity_id(long_id) is False

    def test_uppercase_rejected(self):
        # regex only allows lowercase
        assert validate_entity_id("sensor.Battery_SOC") is False


class TestAddonOptions:
    def test_missing_required_fields(self):
        from sentinel_addon import AddonOptions

        with pytest.raises(ValueError, match="Missing required fields"):
            AddonOptions({})  # missing all fields

        with pytest.raises(ValueError, match="Missing required fields"):
            AddonOptions({"sentinel_host": "bms.sentinel-ai.co.za"})  # missing rest