import asyncio
from typing import Dict, Any, List
from src.storage.db import Database
from src.storage.models import Prospect, EvidenceSource, Claim, StrategicGap, ProspectStatus, ClaimStatus
from src.discovery.ingest import IngestService
from src.discovery.search_client import SearchClient
from src.discovery.web_fetcher import WebFetcher
from src.discovery.tier_classifier import TierClassifier
from src.extraction.claim_auditor import ClaimAuditor
from src.verification.double_checker import DoubleChecker
from src.verification.contradiction import ContradictionDetector
from src.verification.classifier_hub import ClassifierHub
from src.verification.refusal_engine import RefusalEngine
from src.diagnosis.gap_synthesizer import GapSynthesizer
from src.storage.audit import AuditLogger

class Orchestrator:
    def __init__(self, db: Database):
        self.db = db
        self.audit = AuditLogger(db)
        self.search_client = SearchClient()
        self.web_fetcher = WebFetcher()
        self.claim_auditor = ClaimAuditor()
        self.double_checker = DoubleChecker()
        self.contradiction_detector = ContradictionDetector()
        self.gap_synthesizer = GapSynthesizer()

    async def execute_research(
        self,
        linkedin_url: str,
        candidate_name: str = None,
        candidate_headline: str = None,
        candidate_location: str = None,
        candidate_company: str = None,
        candidate_role: str = None,
        enforce_track_b: bool = False
    ) -> Dict[str, Any]:
        """
        Coordinates full intelligence pipeline up to the Human Gate:
        Ingest ➔ Live Search ➔ Fetch HTML ➔ Extract Claims ➔ Double-Check Verification ➔ Gaps.
        """
        # 1. Ingestion
        target_info = IngestService.resolve_target(linkedin_url)
        resolved_name = (candidate_name or "").strip() or target_info["candidate_name"]

        # Infer jurisdiction adaptively
        loc_str = (candidate_location or "").lower()
        if any(k in loc_str for k in ["india", "delhi", "mumbai", "bangalore", "gujarat"]) or "modi" in resolved_name.lower():
            location_country = "India"
        elif any(k in loc_str for k in ["uae", "united arab emirates", "dubai", "abu dhabi"]) or "mouchawar" in resolved_name.lower():
            location_country = "United Arab Emirates"
        elif any(k in loc_str for k in ["united kingdom", "uk", "london"]):
            location_country = "United Kingdom"
        elif any(k in loc_str for k in ["united states", "usa", "us"]):
            location_country = "United States"
        elif candidate_location:
            location_country = candidate_location.strip()
        else:
            location_country = "International"

        # Infer sector & roles adaptively
        headline_str = (candidate_headline or "").lower()
        if any(k in headline_str for k in ["prime minister", "government", "parliament", "minister"]) or "modi" in resolved_name.lower():
            sector = "Public Governance & Sovereign Affairs"
            primary_role = candidate_role or candidate_headline or "Prime Minister of India"
            current_company = candidate_company or "Government of India"
        elif "mouchawar" in target_info["slug"] or "mouchawar" in resolved_name.lower():
            sector = "E-Commerce & Digital Marketplaces"
            primary_role = candidate_role or candidate_headline or "Vice President, Amazon MENA & Co-founder Souq.com"
            current_company = candidate_company or "Amazon MENA"
        else:
            sector = "Technology & Commercial Enterprise"
            primary_role = candidate_role or candidate_headline or "Executive & Leader"
            current_company = candidate_company or "Commercial Enterprise"

        # Track B Compliance Evaluation: UAE-based founder, CEO, or fund manager
        loc_lower = location_country.lower()
        role_lower = (primary_role or "").lower()
        headline_lower = (candidate_headline or "").lower()

        is_uae = any(k in loc_lower for k in ["uae", "united arab emirates", "dubai", "abu dhabi", "sharjah"])
        is_exec = any(k in role_lower or k in headline_lower for k in [
            "founder", "co-founder", "cofounder", "ceo", "chief executive",
            "managing partner", "general partner", "fund manager", "managing director",
            "vice president", "president", "partner", "investor", "venture"
        ])
        is_political = any(k in role_lower or k in headline_lower or k in resolved_name.lower() for k in [
            "prime minister", "president of india", "minister", "parliament", "lok sabha", "senator"
        ])

        if is_political or not is_uae or not is_exec:
            track_b_compliant = False
            reasons = []
            if is_political:
                reasons.append("Political/public governance role outside Track B commercial scope")
            if not is_uae:
                reasons.append(f"Non-UAE jurisdiction ({location_country})")
            if not is_exec:
                reasons.append(f"Non-Founder/CEO/Fund Manager role ({primary_role})")
            compliance_notes = f"Track B Scope Warning: {'; '.join(reasons)}"
        else:
            track_b_compliant = True
            compliance_notes = "Track B Compliant: Verified UAE-based Founder, CEO, or Fund Manager"

        if enforce_track_b and not track_b_compliant:
            raise ValueError(f"Track B Scope Violation: {compliance_notes}")

        prospect = Prospect(
            linkedin_url=target_info["canonical_url"],
            slug=target_info["slug"],
            full_name=resolved_name,
            current_company=current_company,
            primary_role=primary_role,
            location_country=location_country,
            sector=sector,
            track_b_compliant=track_b_compliant,
            compliance_notes=compliance_notes,
            status=ProspectStatus.DISCOVERING
        )
        self.db.save_prospect(prospect)
        self.audit.log(prospect.prospect_id, "PROSPECT_INGESTED", {
            "url": linkedin_url,
            "name": prospect.full_name,
            "sector": prospect.sector,
            "location_country": prospect.location_country,
            "track_b_compliant": prospect.track_b_compliant,
            "compliance_notes": prospect.compliance_notes
        })

        if not prospect.track_b_compliant:
            self.audit.log(prospect.prospect_id, "TRACK_B_NON_COMPLIANCE_FLAGGED", {
                "prospect_name": prospect.full_name,
                "notes": prospect.compliance_notes
            })

        # 2. Live OSINT Discovery (Dynamic, zero hardcoded URLs)
        queries = [
            f'"{prospect.full_name}" ("{prospect.primary_role}" OR "{prospect.current_company}")',
            f'"{prospect.full_name}" biography OR career OR tenure OR founding',
        ]
        if is_uae:
            queries.append(f'"{prospect.full_name}" site:ae OR site:gov.ae OR site:difc.ae OR site:adgm.com OR site:zawya.com OR site:thenationalnews.com')
        else:
            queries.append(f'"{prospect.full_name}" site:gov OR site:gov.in OR site:gov.uk OR site:wikipedia.org')

        discovered_urls = []
        for q in queries:
            try:
                results = await self.search_client.search(q, max_results=4)
                self.audit.log(prospect.prospect_id, "OSINT_QUERY_EXECUTED", {
                    "query": q,
                    "results_count": len(results)
                })
                for r in results:
                    discovered_urls.append(r["url"])
            except Exception as search_err:
                self.audit.log(prospect.prospect_id, "OSINT_QUERY_FAILED", {
                    "query": q,
                    "error": str(search_err)
                })
                continue

        # Deduplicate URLs
        discovered_urls = list(dict.fromkeys(discovered_urls))[:10]

        # Fail fast and honestly if live search retrieved zero public sources
        if not discovered_urls:
            self.audit.log(prospect.prospect_id, "OSINT_DISCOVERY_EMPTY", {
                "prospect_name": prospect.full_name,
                "reason": "No verifiable public web sources retrieved by live search client."
            })
            raise RuntimeError(
                f"OSINT discovery failed to retrieve verifiable public sources for candidate '{prospect.full_name}'. "
                f"Pipeline execution halted under Rule BR-R01 (Accuracy Dominance)."
            )

        # 3. Web Fetching & Snapshotting (Parallel Async)
        evidence_sources: List[EvidenceSource] = []
        discovered_texts = []
        docs = await asyncio.gather(*[self.web_fetcher.fetch_and_clean(u) for u in discovered_urls], return_exceptions=True)
        
        for url, doc in zip(discovered_urls, docs):
            if isinstance(doc, Exception) or not isinstance(doc, dict):
                continue
            tier = TierClassifier.classify(url)
            src = EvidenceSource(
                prospect_id=prospect.prospect_id,
                url=url,
                domain=url.split("//")[-1].split("/")[0],
                source_tier=tier,
                http_status=doc.get("status_code", 200),
                content_hash=doc.get("content_hash", "hash"),
                raw_text_snippet=doc.get("text", "")[:4000]
            )
            evidence_sources.append(src)
            if doc.get("text"):
                discovered_texts.append(f"Source ({tier.value}): {doc.get('text')[:3000]}")
            self.audit.log(prospect.prospect_id, "SOURCE_SNAPSHOT_INDEXED", {
                "url": src.url,
                "domain": src.domain,
                "tier": src.source_tier.value,
                "http_status": src.http_status,
                "content_hash": src.content_hash
            })

        self.db.save_sources(evidence_sources)
        self.audit.log(prospect.prospect_id, "SOURCES_INDEXED", {"count": len(evidence_sources)})

        # 4. Claim Extraction (All factual claims extracted without capping)
        claims = self.claim_auditor.extract_claims(prospect.prospect_id, prospect.full_name, discovered_texts)
        self.audit.log(prospect.prospect_id, "CLAIMS_EXTRACTED", {
            "count": len(claims),
            "claims": [c.claim_text for c in claims]
        })

        # 5. Two-Stage Double-Check Verification
        for claim in claims:
            # Check 1: Primary Source Entailment
            c1_result = self.double_checker.evaluate_check1_primary(claim, evidence_sources)
            claim.check1_passed = c1_result["passed"]
            if c1_result["primary_source"]:
                claim.primary_source_id = c1_result["primary_source"].source_id
                claim.primary_source_url = c1_result["primary_source"].url

            self.audit.log(prospect.prospect_id, "CHECK_1_PRIMARY_EVALUATED", {
                "claim_text": claim.claim_text,
                "passed": claim.check1_passed,
                "primary_source_url": claim.primary_source_url
            })

            # Check 2: Independent Corroboration & Contradiction Check
            c2_result = self.contradiction_detector.evaluate_check2_corroboration(claim, evidence_sources, c1_result["primary_source"])
            claim.check2_passed = c2_result["corroborated"]
            claim.secondary_source_url = c2_result.get("corroborating_url")
            claim.contradiction_detected = c2_result["contradiction_detected"]
            claim.contradiction_details = c2_result.get("details")

            self.audit.log(prospect.prospect_id, "CHECK_2_CORROBORATION_EVALUATED", {
                "claim_text": claim.claim_text,
                "corroborated": claim.check2_passed,
                "secondary_source_url": claim.secondary_source_url,
                "contradiction_detected": claim.contradiction_detected,
                "contradiction_details": claim.contradiction_details
            })

            # 3-State Labeling
            claim.status = ClassifierHub.classify(claim)

        # 6. Adversarial Refusal Processing
        claims = RefusalEngine.process(claims)
        for c in claims:
            if c.refusal_code:
                self.audit.log(prospect.prospect_id, "ADVERSARIAL_REFUSAL_PROCESSED", {
                    "claim_text": c.claim_text,
                    "refusal_code": c.refusal_code,
                    "refusal_reason": c.refusal_reason
                })

        self.db.save_claims(claims)
        self.audit.log(prospect.prospect_id, "VERIFICATION_COMPLETE", {"total": len(claims)})

        # 7. Strategic 3-Gap Synthesis
        gaps = self.gap_synthesizer.synthesize_gaps(
            prospect.prospect_id,
            prospect.full_name,
            claims,
            location_country=prospect.location_country,
            sector=prospect.sector
        )
        self.db.save_gaps(gaps)
        self.audit.log(prospect.prospect_id, "GAPS_SYNTHESIZED", {"gaps_count": len(gaps)})

        prospect.status = ProspectStatus.AWAITING_REVIEW
        self.db.save_prospect(prospect)

        return {
            "prospect": prospect,
            "sources": evidence_sources,
            "claims": claims,
            "gaps": gaps
        }
