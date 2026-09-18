import pytest
from src.discovery.tier_classifier import TierClassifier
from src.storage.models import SourceTier

def test_tier1_global_government_domains():
    # India sovereign
    assert TierClassifier.classify("https://www.pmindia.gov.in/en/") == SourceTier.TIER_1_PRIMARY
    assert TierClassifier.classify("https://india.gov.in/my-government/prime-minister") == SourceTier.TIER_1_PRIMARY
    assert TierClassifier.classify("https://sansad.in/ls") == SourceTier.TIER_1_PRIMARY
    assert TierClassifier.classify("https://mca.gov.in/content/mca/global/en/home.html") == SourceTier.TIER_1_PRIMARY
    assert TierClassifier.classify("https://meity.nic.in/profile") == SourceTier.TIER_1_PRIMARY

    # US sovereign
    assert TierClassifier.classify("https://www.sec.gov/edgar") == SourceTier.TIER_1_PRIMARY
    assert TierClassifier.classify("https://www.whitehouse.gov/briefing-room") == SourceTier.TIER_1_PRIMARY
    
    # UK sovereign
    assert TierClassifier.classify("https://www.gov.uk/government/organisations") == SourceTier.TIER_1_PRIMARY
    assert TierClassifier.classify("https://parliament.uk") == SourceTier.TIER_1_PRIMARY

    # UAE sovereign
    assert TierClassifier.classify("https://u.ae/en/information-and-services") == SourceTier.TIER_1_PRIMARY
    assert TierClassifier.classify("https://www.adgm.com/public-registers") == SourceTier.TIER_1_PRIMARY
    assert TierClassifier.classify("https://www.difc.ae/public-register") == SourceTier.TIER_1_PRIMARY

def test_tier1_academic_and_corporate():
    assert TierClassifier.classify("https://www.harvard.edu/president") == SourceTier.TIER_1_PRIMARY
    assert TierClassifier.classify("https://www.ox.ac.uk/about") == SourceTier.TIER_1_PRIMARY
    assert TierClassifier.classify("https://iitd.ac.in/") == SourceTier.TIER_1_PRIMARY
    assert TierClassifier.classify("https://press.aboutamazon.com/2017/3/amazon-to-acquire-souq-com") == SourceTier.TIER_1_PRIMARY

def test_tier2_reputable_press():
    assert TierClassifier.classify("https://www.bloomberg.com/news/articles/2024-01-01") == SourceTier.TIER_2_SECONDARY
    assert TierClassifier.classify("https://www.reuters.com/world/india/modi-wins-election") == SourceTier.TIER_2_SECONDARY
    assert TierClassifier.classify("https://economictimes.indiatimes.com/news/india") == SourceTier.TIER_2_SECONDARY
    assert TierClassifier.classify("https://www.thehindu.com/news/national/") == SourceTier.TIER_2_SECONDARY

def test_tier3_aggregators():
    assert TierClassifier.classify("https://en.wikipedia.org/wiki/Narendra_Modi") == SourceTier.TIER_3_AGGREGATOR
    assert TierClassifier.classify("https://www.crunchbase.com/person/ronaldo-mouchawar") == SourceTier.TIER_3_AGGREGATOR

def test_tier4_social_and_blogs():
    assert TierClassifier.classify("https://x.com/narendramodi") == SourceTier.TIER_4_SOCIAL
    assert TierClassifier.classify("https://medium.com/@random_user/my-thoughts") == SourceTier.TIER_4_SOCIAL
