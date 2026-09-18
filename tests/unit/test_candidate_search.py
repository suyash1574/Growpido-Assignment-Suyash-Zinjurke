import pytest
from src.discovery.candidate_search import CandidateSearchEngine
from src.storage.models import CandidateMatch

def test_extract_candidate_from_linkedin_title():
    engine = CandidateSearchEngine(use_live_search=False)
    
    title = "Ronaldo Mouchawar - Vice President - Amazon | LinkedIn"
    url = "https://ae.linkedin.com/in/ronaldo-mouchawar-souq"
    snippet = "Ronaldo Mouchawar is the Vice President of Amazon MENA and co-founder of Souq.com based in Dubai, UAE."
    
    candidate = engine._parse_candidate_result(title, url, snippet)
    assert candidate is not None
    assert "ronaldo-mouchawar-souq" in candidate.linkedin_url
    assert "https://www.linkedin.com/in/ronaldo-mouchawar-souq" == candidate.linkedin_url
    assert candidate.full_name == "Ronaldo Mouchawar"
    assert "Vice President" in candidate.headline or "Amazon" in candidate.headline

def test_extract_candidate_narendra_modi():
    engine = CandidateSearchEngine(use_live_search=False)
    
    title = "Narendra Modi - Prime Minister of India | LinkedIn"
    url = "https://in.linkedin.com/in/narendramodi"
    snippet = "Narendra Modi is the Prime Minister of India since 2014. Located in New Delhi, India."
    
    candidate = engine._parse_candidate_result(title, url, snippet)
    assert candidate is not None
    assert candidate.linkedin_url == "https://www.linkedin.com/in/narendramodi"
    assert "Narendra Modi" in candidate.full_name
    assert "Prime Minister" in candidate.headline

def test_candidate_query_construction():
    engine = CandidateSearchEngine(use_live_search=False)
    query = engine.build_search_query("Narendra Modi", "Prime Minister India")
    assert 'site:linkedin.com/in/' in query
    assert '"Narendra Modi"' in query
    assert "Prime Minister India" in query
