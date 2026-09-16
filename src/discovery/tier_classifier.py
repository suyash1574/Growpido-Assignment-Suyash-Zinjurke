from urllib.parse import urlparse
from src.storage.models import SourceTier

# Tier 1 Whitelist Patterns: Official Registries & Primary Corporate Disclosures
TIER_1_PATTERNS = [
    # Government & Regulatory
    "gov.ae", "adgm.com", "difc.ae", "dfsa.ae", "moec.gov.ae", "sec.gov",
    # Corporate primary domains / investor relations
    "press.aboutamazon.com", "aboutamazon.com", "amazon.ae", "souq.com", "ir.aboutamazon.com"
]

# Tier 2 Whitelist Patterns: Reputable Business & Financial Press
TIER_2_PATTERNS = [
    "bloomberg.com", "reuters.com", "ft.com", "forbesmiddleeast.com",
    "thenationalnews.com", "gulfnews.com", "arabianbusiness.com",
    "wam.ae", "zawya.com", "khaleejtimes.com"
]

# Tier 3 Aggregator Patterns: Directories & Wikilinks (Discovery only, never primary verification)
TIER_3_PATTERNS = [
    "wikipedia.org", "crunchbase.com", "pitchbook.com", "zoominfo.com",
    "rocketreach.co", "theorg.com", "dealroom.co"
]

class TierClassifier:
    @staticmethod
    def classify(url: str) -> SourceTier:
        try:
            domain = urlparse(url).netloc.lower()
            if domain.startswith("www."):
                domain = domain[4:]

            # Check Tier 1
            for pattern in TIER_1_PATTERNS:
                if domain == pattern or domain.endswith("." + pattern):
                    return SourceTier.TIER_1_PRIMARY

            # Check Tier 2
            for pattern in TIER_2_PATTERNS:
                if domain == pattern or domain.endswith("." + pattern):
                    return SourceTier.TIER_2_SECONDARY

            # Check Tier 3
            for pattern in TIER_3_PATTERNS:
                if domain == pattern or domain.endswith("." + pattern):
                    return SourceTier.TIER_3_AGGREGATOR

            # Check Academic (.edu / .ac.ae) -> Tier 1
            if domain.endswith(".edu") or domain.endswith(".ac.ae"):
                return SourceTier.TIER_1_PRIMARY

            # Default to Tier 4 (Unverified / Social / Blog)
            return SourceTier.TIER_4_SOCIAL
        except Exception:
            return SourceTier.TIER_4_SOCIAL
