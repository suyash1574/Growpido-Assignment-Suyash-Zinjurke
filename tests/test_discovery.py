import pytest
from src.discovery.tier_classifier import TierClassifier
from src.storage.models import SourceTier

def test_tier_1_registries():
    assert TierClassifier.classify("https://www.adgm.com/public-registers/companies") == SourceTier.TIER_1_PRIMARY
    assert TierClassifier.classify("https://www.difc.ae/public-register/entity/123") == SourceTier.TIER_1_PRIMARY
    assert TierClassifier.classify("https://press.aboutamazon.com/2017/3/amazon-to-acquire-souq") == SourceTier.TIER_1_PRIMARY
    assert TierClassifier.classify("https://www.sec.gov/edgar/browse") == SourceTier.TIER_1_PRIMARY

def test_tier_2_press():
    assert TierClassifier.classify("https://www.bloomberg.com/news/articles/2021-05-12/amazon-souq") == SourceTier.TIER_2_SECONDARY
    assert TierClassifier.classify("https://www.reuters.com/article/souq-amazon") == SourceTier.TIER_2_SECONDARY
    assert TierClassifier.classify("https://www.thenationalnews.com/business") == SourceTier.TIER_2_SECONDARY

def test_tier_3_aggregators():
    assert TierClassifier.classify("https://en.wikipedia.org/wiki/Ronaldo_Mouchawar") == SourceTier.TIER_3_AGGREGATOR
    assert TierClassifier.classify("https://www.crunchbase.com/person/ronaldo-mouchawar") == SourceTier.TIER_3_AGGREGATOR

def test_tier_4_social():
    assert TierClassifier.classify("https://medium.com/@randomuser/my-thoughts") == SourceTier.TIER_4_SOCIAL
    assert TierClassifier.classify("https://twitter.com/post/123456") == SourceTier.TIER_4_SOCIAL
