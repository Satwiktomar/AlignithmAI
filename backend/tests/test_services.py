"""Unit tests for backend services."""
import pytest
from app.services.parser import extract_text, extract_text_from_pdf
from app.services.gemini import extract_json, _is_quota_error
from app.services.auth import encrypt_api_key, decrypt_api_key


class TestParser:
    def test_extract_text_from_txt(self):
        content = b"Hello World\nLine 2"
        result = extract_text("test.txt", content)
        assert "Hello World" in result
        assert "Line 2" in result

    def test_extract_text_from_unknown_falls_back(self):
        content = b"Some text content"
        result = extract_text("test.xyz", content)
        assert "Some text content" in result

    def test_extract_text_empty_file(self):
        result = extract_text("test.txt", b"")
        assert result == ""

    def test_extract_text_unicode(self):
        content = "Héllo Wörld café".encode("utf-8")
        result = extract_text("test.txt", content)
        assert "Héllo" in result


class TestExtractJson:
    def test_valid_json(self):
        result = extract_json('{"key": "value"}')
        assert result == {"key": "value"}

    def test_json_in_code_block(self):
        text = '```json\n{"key": "value"}\n```'
        result = extract_json(text)
        assert result == {"key": "value"}

    def test_json_in_plain_code_block(self):
        text = '```\n{"key": "value"}\n```'
        result = extract_json(text)
        assert result == {"key": "value"}

    def test_json_embedded_in_text(self):
        text = 'Some text before {"key": "value"} and after'
        result = extract_json(text)
        assert result == {"key": "value"}

    def test_invalid_json(self):
        result = extract_json("not json at all")
        assert "error" in result
        assert "raw" in result

    def test_json_array(self):
        result = extract_json('[1, 2, 3]')
        assert result == [1, 2, 3]


class TestQuotaError:
    def test_429_detected(self):
        assert _is_quota_error(Exception("HTTP 429 Too Many Requests"))

    def test_resource_exhausted_detected(self):
        assert _is_quota_error(Exception("RESOURCE_EXHAUSTED"))

    def test_quota_detected(self):
        assert _is_quota_error(Exception("Quota exceeded for default model"))

    def test_non_quota_error(self):
        assert not _is_quota_error(Exception("Connection timeout"))
        assert not _is_quota_error(Exception("Invalid API key"))


class TestApiKeyCrypto:
    def test_encrypt_decrypt_roundtrip(self):
        original = "AIzaSyB_test_key_12345"
        encrypted = encrypt_api_key(original)
        assert encrypted != original
        decrypted = decrypt_api_key(encrypted)
        assert decrypted == original

    def test_decrypt_none_returns_none(self):
        result = decrypt_api_key(None)
        assert result is None

    def test_decrypt_invalid_returns_none(self):
        result = decrypt_api_key("not-a-valid-encrypted-string")
        assert result is None

    def test_different_keys_produce_different_ciphertexts(self):
        key1 = encrypt_api_key("key_one")
        key2 = encrypt_api_key("key_two")
        assert key1 != key2


class TestScraper:
    def test_validate_url_blocks_private_ip(self):
        from app.services.scraper import _validate_url
        from fastapi import HTTPException
        with pytest.raises(HTTPException) as exc_info:
            _validate_url("http://127.0.0.1/admin")
        assert exc_info.value.status_code == 400
        assert "private" in exc_info.value.detail.lower() or "internal" in exc_info.value.detail.lower()

    def test_validate_url_blocks_bad_scheme(self):
        from app.services.scraper import _validate_url
        from fastapi import HTTPException
        with pytest.raises(HTTPException) as exc_info:
            _validate_url("ftp://example.com/file")
        assert exc_info.value.status_code == 400

    def test_validate_url_allows_public(self):
        from app.services.scraper import _validate_url
        result = _validate_url("https://www.linkedin.com/jobs/123")
        assert result == "https://www.linkedin.com/jobs/123"


class TestGetAiConfig:
    """Tests for the get_ai_config() provider-routing helper."""

    def test_gemini_provider_returns_gemini_key(self):
        from app.services.gemini import get_ai_config
        from app.services.auth import encrypt_api_key

        class FakeUser:
            ai_provider = "gemini"
            gemini_api_key = encrypt_api_key("test-gemini-key")
            openai_api_key = encrypt_api_key("test-openai-key")

        key, provider = get_ai_config(FakeUser())
        assert provider == "gemini"
        assert key == "test-gemini-key"

    def test_openai_provider_returns_openai_key(self):
        from app.services.gemini import get_ai_config
        from app.services.auth import encrypt_api_key

        class FakeUser:
            ai_provider = "openai"
            gemini_api_key = encrypt_api_key("test-gemini-key")
            openai_api_key = encrypt_api_key("test-openai-key")

        key, provider = get_ai_config(FakeUser())
        assert provider == "openai"
        assert key == "test-openai-key"

    def test_no_provider_defaults_to_gemini(self):
        from app.services.gemini import get_ai_config

        class FakeUser:
            ai_provider = None
            gemini_api_key = None
            openai_api_key = None

        key, provider = get_ai_config(FakeUser())
        assert provider == "gemini"
        assert key is None

    def test_missing_ai_provider_attr_defaults_to_gemini(self):
        from app.services.gemini import get_ai_config

        class FakeUser:
            gemini_api_key = None

        key, provider = get_ai_config(FakeUser())
        assert provider == "gemini"


class TestOpenAIQuotaError:
    """Tests for _is_openai_quota_error() detection."""

    def test_429_detected(self):
        from app.services.openai_service import _is_openai_quota_error
        assert _is_openai_quota_error(Exception("Error 429 rate limit"))

    def test_rate_limit_detected(self):
        from app.services.openai_service import _is_openai_quota_error
        assert _is_openai_quota_error(Exception("rate_limit_exceeded"))

    def test_insufficient_quota_detected(self):
        from app.services.openai_service import _is_openai_quota_error
        assert _is_openai_quota_error(Exception("insufficient_quota"))

    def test_non_quota_error(self):
        from app.services.openai_service import _is_openai_quota_error
        assert not _is_openai_quota_error(Exception("Connection refused"))
        assert not _is_openai_quota_error(Exception("Invalid API key"))

