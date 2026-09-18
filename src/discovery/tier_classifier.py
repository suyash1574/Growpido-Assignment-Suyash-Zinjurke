import re
from urllib.parse import urlparse
from src.storage.models import SourceTier

# Tier 1 Specific Recognized Domains: Official Registries, Sovereign Portals & Corporate IR
TIER_1_SPECIFIC_DOMAINS = [
    # Sovereign / State Portals
    "u.ae", "sansad.in", "parliament.uk", "whitehouse.gov", "pmindia.gov.in", "india.gov.in",
    "adgm.com", "difc.ae", "dfsa.ae", "moec.gov.ae", "sec.gov", "mca.gov.in", "companieshouse.gov.uk",
    # Corporate primary domains / investor relations
    "press.aboutamazon.com", "aboutamazon.com", "amazon.ae", "souq.com", "ir.aboutamazon.com"
]

# Tier 2 Whitelist Patterns: Reputable Business, Financial, and National News Media
TIER_2_PATTERNS = [
    "bloomberg.com", "reuters.com", "ft.com", "wsj.com", "cnbc.com", "bbc.com",
    "thehindu.com", "indiatimes.com", "economictimes.com", "hindustantimes.com",
    "indianexpress.com", "ndtv.com", "forbesmiddleeast.com", "forbes.com",
    "thenationalnews.com", "gulfnews.com", "arabianbusiness.com", "wam.ae",
    "zawya.com", "khaleejtimes.com"
]

# Tier 3 Aggregator Patterns: Directories & Wikilinks (Discovery only, never primary verification)
TIER_3_PATTERNS = [
    "wikipedia.org", "crunchbase.com", "pitchbook.com", "zoominfo.com",
    "rocketreach.co", "theorg.com", "dealroom.co"
]

class TierClassifier:
    """
    Forensic classifier categorizing web sources into four hierarchical authority tiers:
    Tier 1: Sovereign government registries, state gazettes, verified corporate domains, accredited universities
    Tier 2: Reputable global and national financial & wire press
    Tier 3: Aggregators, directories, and wikis (discovery only)
    Tier 4: Social media, unverified blogs, and forums (quarantined)
    """

    @staticmethod
    def classify(url: str) -> SourceTier:
        try:
            domain = urlparse(url).netloc.lower()
            if domain.startswith("www."):
                domain = domain[4:]

            # 1. Check Specific Known Tier 1 Domains
            for pattern in TIER_1_SPECIFIC_DOMAINS:
                if domain == pattern or domain.endswith("." + pattern):
                    return SourceTier.TIER_1_PRIMARY

            # 2. Universal Sovereign Government Domain Patterns (Worldwide)
            # Matches: gov.uk, .gov, .gov.in, .gov.ae, .gov.au, .gov.sg, etc.
            if domain == "gov" or domain.endswith(".gov") or re.search(r"(?:^|\.)gov\.[a-z]{2,4}$", domain):
                return SourceTier.TIER_1_PRIMARY

            # Matches: .nic.in, .nic.<cc>, .mil, .mil.<cc>, parliament.<cc>
            if domain.startswith("nic.") or domain.endswith(".nic.in") or re.search(r"(?:^|\.)nic\.[a-z]{2,4}$", domain):
                return SourceTier.TIER_1_PRIMARY
            if domain.endswith(".mil") or re.search(r"(?:^|\.)mil\.[a-z]{2,4}$", domain):
                return SourceTier.TIER_1_PRIMARY
            if re.search(r"(?:^|\.)parliament\.[a-z]{2,4}$", domain) or domain == "parliament.uk":
                return SourceTier.TIER_1_PRIMARY

            # 3. Universal Academic / University Institutions (.edu, .edu.<cc>, .ac.<cc>)
            if domain.endswith(".edu") or re.search(r"\.edu\.[a-z]{2,4}$", domain) or re.search(r"\.ac\.[a-z]{2,4}$", domain):
                return SourceTier.TIER_1_PRIMARY

            # 4. Check Tier 2 Reputable Media
            for pattern in TIER_2_PATTERNS:
                if domain == pattern or domain.endswith("." + pattern):
                    return SourceTier.TIER_2_SECONDARY

            # 5. Check Tier 3 Aggregators
            for pattern in TIER_3_PATTERNS:
                if domain == pattern or domain.endswith("." + pattern):
                    return SourceTier.TIER_3_AGGREGATOR

            # Default to Tier 4 (Unverified / Social / Blog)
            return SourceTier.TIER_4_SOCIAL
        except Exception:
            return SourceTier.TIER_4_SOCIAL
