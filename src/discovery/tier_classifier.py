import re
from urllib.parse import urlparse
from src.storage.models import SourceTier

# Tier 1 Specific Recognized Domains: Official Registries, Sovereign Portals & Corporate IR
TIER_1_SPECIFIC_DOMAINS = [
    # Sovereign / State Portals & Exchanges
    "u.ae", "sansad.in", "parliament.uk", "whitehouse.gov", "pmindia.gov.in", "india.gov.in",
    "adgm.com", "difc.ae", "dfsa.ae", "moec.gov.ae", "sec.gov", "mca.gov.in", "companieshouse.gov.uk",
    "mediaoffice.ae", "dfm.ae", "adx.ae", "cbuae.gov.ae", "centralbank.ae", "sca.gov.ae",
    "dubaided.gov.ae", "ded.ae", "abudhabi.ae", "dubai.ae",
    # Corporate primary domains / investor relations / banking & enterprise
    "press.aboutamazon.com", "aboutamazon.com", "aboutamazon.me", "amazon.com", "amazon.ae", "souq.com", "ir.aboutamazon.com",
    "cbiuae.com", "cbi.ae", "bankfab.com", "emiratesnbd.com", "mashreqbank.com", "adcb.com", "dib.ae", "rakbank.ae",
    "careem.com", "emaar.com", "aldar.com", "damacproperties.com", "kitopi.com", "swvl.com", "anghami.com",
    "bayut.com", "propertyfinder.ae", "tabby.ai", "tamara.co", "global.vc", "dhamani1969.com",
    "growpido.com", "openai.com", "microsoft.com", "google.com", "deepmind.com", "stanford.edu", "nvidia.com", "amd.com", "apple.com", "tesla.com"
]

# Tier 2 Whitelist Patterns: Reputable Business, Financial, and National News Media
TIER_2_PATTERNS = [
    "bloomberg.com", "reuters.com", "ft.com", "wsj.com", "cnbc.com", "bbc.com",
    "thehindu.com", "indiatimes.com", "economictimes.com", "hindustantimes.com",
    "indianexpress.com", "ndtv.com", "forbesmiddleeast.com", "forbes.com",
    "thenationalnews.com", "gulfnews.com", "arabianbusiness.com", "wam.ae",
    "zawya.com", "khaleejtimes.com", "gulfbusiness.com", "entrepreneur.com",
    "arabnews.com", "businessoffashion.com", "aljazeera.com", "meed.com",
    "fastcompany.com", "techcrunch.com", "inc.com", "wamda.com", "magnitt.com",
    "cision.com", "prnewswire.com", "businesswire.com", "globenewswire.com",
    "marketscreener.com", "northdata.com", "equilar.com"
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
    def classify(url: str, corporate_domain: str = None, company_name: str = None) -> SourceTier:
        try:
            domain = urlparse(url).netloc.lower()
            if domain.startswith("www."):
                domain = domain[4:]

            # Check explicit corporate domain match if passed
            if corporate_domain:
                cd = corporate_domain.lower().replace("www.", "").strip()
                if cd and (domain == cd or domain.endswith("." + cd)):
                    return SourceTier.TIER_1_PRIMARY

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

            # 4. Check Tier 2 Reputable Media & Commercial Wire Records
            for pattern in TIER_2_PATTERNS:
                if domain == pattern or domain.endswith("." + pattern):
                    return SourceTier.TIER_2_SECONDARY

            # 5. Check Tier 3 Aggregators
            for pattern in TIER_3_PATTERNS:
                if domain == pattern or domain.endswith("." + pattern):
                    return SourceTier.TIER_3_AGGREGATOR

            # 6. Dynamic Operating Company Matching (Candidate's Official Corporate Portal)
            is_social = any(s in domain for s in ["linkedin.com", "twitter.com", "x.com", "facebook.com", "instagram.com", "medium.com", "youtube.com", "tiktok.com", "reddit.com"])
            if company_name and not is_social:
                cleaned_comp = re.sub(r"[^a-zA-Z0-9]", "", company_name.lower())
                # Generate acronym (e.g. Commercial Bank International -> cbi)
                words = [w for w in company_name.lower().split() if w not in ["the", "and", "of", "ltd", "llc", "corp", "inc", "co"]]
                acronym = "".join(w[0] for w in words if len(w) > 0)
                
                domain_clean = re.sub(r"[^a-zA-Z0-9]", "", domain)
                if len(cleaned_comp) >= 4 and cleaned_comp in domain_clean:
                    return SourceTier.TIER_1_PRIMARY
                if len(acronym) >= 3 and acronym in domain:
                    return SourceTier.TIER_1_PRIMARY

            # 7. Official Corporate Press Releases & Investor Relations Portals
            if not is_social:
                lower_url = url.lower()
                if any(p in lower_url for p in ["/press", "/news-release", "/investor", "/corporate-governance", "/board-of-directors"]):
                    return SourceTier.TIER_1_PRIMARY

            # Default to Tier 4 (Unverified / Social / Blog)
            return SourceTier.TIER_4_SOCIAL
        except Exception:
            return SourceTier.TIER_4_SOCIAL
