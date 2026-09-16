import pytest
from src.discovery.ingest import IngestService

def test_valid_linkedin_urls():
    assert IngestService.validate_url("https://www.linkedin.com/in/ronaldo-mouchawar-souq")
    assert IngestService.validate_url("https://linkedin.com/in/john-doe-123/")
    assert IngestService.validate_url("https://www.linkedin.com/in/jane_doe")

def test_invalid_linkedin_urls():
    assert not IngestService.validate_url("https://linkedin.com/feed/")
    assert not IngestService.validate_url("https://google.com")
    assert not IngestService.validate_url("ftp://linkedin.com/in/test")
    assert not IngestService.validate_url("")

def test_slug_parsing():
    slug = IngestService.parse_slug("https://www.linkedin.com/in/ronaldo-mouchawar-souq/")
    assert slug == "ronaldo-mouchawar-souq"

def test_target_resolution():
    res = IngestService.resolve_target("https://www.linkedin.com/in/ronaldo-mouchawar-souq")
    assert res["candidate_name"] == "Ronaldo Mouchawar"
    assert res["canonical_url"] == "https://www.linkedin.com/in/ronaldo-mouchawar-souq"
