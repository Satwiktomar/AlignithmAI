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
