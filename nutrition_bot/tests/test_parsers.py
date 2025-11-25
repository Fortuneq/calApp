import pytest
from datetime import datetime
from utils.parsers import (
    parse_manual_entry,
    extract_grams,
    validate_grams,
    sanitize_dish_name
)


class TestManualEntryParser:
    """Test manual entry command parser"""

    def test_parse_simple_entry(self):
        """Test basic /v command"""
        result = parse_manual_entry("/v яблоко 150")
        assert result is not None
        dish, grams, eaten_at = result
        assert dish == "яблоко"
        assert grams == 150
        assert isinstance(eaten_at, datetime)

    def test_parse_with_time(self):
        """Test /v command with time"""
        result = parse_manual_entry("/v греча 200 18:30")
        assert result is not None
        dish, grams, eaten_at = result
        assert dish == "греча"
        assert grams == 200
        assert eaten_at.hour == 18
        assert eaten_at.minute == 30

    def test_parse_with_grams_suffix(self):
        """Test /v command with 'г' suffix"""
        result = parse_manual_entry("/v курица 180г")
        assert result is not None
        dish, grams, eaten_at = result
        assert dish == "курица"
        assert grams == 180

    def test_parse_invalid_format(self):
        """Test invalid command format"""
        result = parse_manual_entry("/v")
        assert result is None

        result = parse_manual_entry("/v яблоко")
        assert result is None

    def test_parse_invalid_grams(self):
        """Test invalid grams"""
        result = parse_manual_entry("/v яблоко abc")
        assert result is None


class TestGramsExtraction:
    """Test grams extraction from text"""

    def test_extract_number_only(self):
        """Test extraction of plain number"""
        assert extract_grams("150") == 150
        assert extract_grams("200") == 200

    def test_extract_with_suffix(self):
        """Test extraction with 'г' suffix"""
        assert extract_grams("150г") == 150
        assert extract_grams("200 г") == 200

    def test_extract_invalid(self):
        """Test invalid input"""
        assert extract_grams("abc") is None
        assert extract_grams("") is None


class TestGramsValidation:
    """Test grams validation"""

    def test_valid_range(self):
        """Test valid grams range"""
        assert validate_grams(1) is True
        assert validate_grams(100) is True
        assert validate_grams(5000) is True

    def test_invalid_range(self):
        """Test invalid grams range"""
        assert validate_grams(0) is False
        assert validate_grams(-10) is False
        assert validate_grams(5001) is False


class TestDishNameSanitization:
    """Test dish name sanitization"""

    def test_basic_sanitization(self):
        """Test basic cleaning"""
        assert sanitize_dish_name("яблоко") == "Яблоко"
        assert sanitize_dish_name("ГРЕЧА") == "Греча"

    def test_whitespace_removal(self):
        """Test whitespace handling"""
        assert sanitize_dish_name("  яблоко  ") == "Яблоко"
        assert sanitize_dish_name("яблоко   зеленое") == "Яблоко зеленое"

    def test_max_length(self):
        """Test max length constraint"""
        long_name = "а" * 300
        result = sanitize_dish_name(long_name)
        assert len(result) <= 255


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
