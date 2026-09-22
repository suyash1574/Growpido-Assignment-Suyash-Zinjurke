import json
from uuid import UUID
from typing import List, Optional, Any
from src.llm_client import llm_client, UnifiedLLMClient
from src.storage.models import StrategicGap, GapDimension, Claim, ClaimStatus

class GapSynthesizer:
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        if api_key or model:
            self.client = UnifiedLLMClient(groq_api_key=api_key, groq_model=model)
        else:
            self.client = llm_client

    def synthesize_gaps(
        self,
        prospect_id: UUID,
        candidate_name: str,
        verified_claims: List[Claim],
        location_country: str = "UAE",
        sector: str = "Executive Leadership",
        evidence_sources: List[Any] = None
    ) -> List[StrategicGap]:
        """
        Synthesizes exactly three prioritized strategic presence gaps comparing verified facts
        against public executive positioning, adapted to the prospect's actual jurisdiction and sector.
        1. Authority Under-Indexing
        2. Channel Diversity Deficit
        3. Narrative Fragmentation
        """
        facts_summary = "\n".join([f"- {c.claim_text} ({c.category.value})" for c in verified_claims if c.status == ClaimStatus.VERIFIED])
        if not facts_summary:
            facts_summary = f"- Prominent {location_country} leader with emerging digital footprint: {candidate_name} ({sector})"

        default_gaps = [
            StrategicGap(
                prospect_id=prospect_id,
                rank=1,
                dimension=GapDimension.AUTHORITY_UNDER_INDEXING,
                title="Unleveraged Institutional Milestone Authority",
                observation=f"{candidate_name}'s verified career milestones in {sector} remain concentrated in secondary corporate coverage rather than an indexed, authoritative executive archive.",
                strategic_impact="Restricts inbound institutional partnership and strategic co-investment deal flow.",
                recommendation=f"Establish a sovereign executive web domain housing verified career case studies, exits, and governance mandates within {location_country} and globally."
            ),
            StrategicGap(
                prospect_id=prospect_id,
                rank=2,
                dimension=GapDimension.CHANNEL_DIVERSITY_DEFICIT,
                title="Concentrated Third-Party Channel Reliance",
                observation=f"Public executive positioning for {candidate_name} is mediated primarily through third-party news citations rather than direct, authored policy and business perspectives.",
                strategic_impact="Leaves market perception dependent on sporadic media coverage rather than proactive strategic narrative framing.",
                recommendation=f"Syndicate regular thought-leadership columns and official addresses into Tier-1 regional business and trade publications covering {location_country}."
            ),
            StrategicGap(
                prospect_id=prospect_id,
                rank=3,
                dimension=GapDimension.NARRATIVE_FRAGMENTATION,
                title="Operational vs. Strategic Governance Narrative Tension",
                observation=f"Publicly accessible records emphasize tactical operational events without a clearly codified, long-term strategic and institutional advisory thesis.",
                strategic_impact="Creates ambiguity regarding commercial focus, advisory capacity, and institutional mandate.",
                recommendation="Codify a distinct 'Executive Fellowship & Advisory Philosophy' narrative pillar separate from day-to-day operational duties."
            )
        ]

        if not self.client:
            return default_gaps

        channels_found = ["linkedin.com"]  # Prospect always has a LinkedIn URL provided
        if evidence_sources:
            channels_found.extend([s.domain for s in evidence_sources if s.domain])
        channels_found = list(set(channels_found))
        channel_context = f"Measured Channel Footprint: {', '.join(channels_found)}"

        prompt = (
            f"You are Growpido's Principal Executive Branding Strategist.\n"
            f"Analyze the verified achievements of {location_country} {sector} leader: {candidate_name}.\n\n"
            f"Verified Facts:\n{facts_summary}\n\n"
            f"Operating Jurisdiction: {location_country}\n"
            f"Primary Sector: {sector}\n"
            f"{channel_context}\n\n"
            "STRICT EVIDENCE GROUNDING RULES:\n"
            "1. Base observations strictly on the provided verified facts and the Measured Channel Footprint.\n"
            "2. DO NOT mention specific platforms like YouTube, Instagram, BCG, or CEO Works unless they are explicitly present in the Verified Facts or Measured Channel Footprint.\n"
            "3. DO NOT invent or speculate about absent channels. You must NOT claim an entity or platform is absent, only that the measured footprint is limited to what is documented.\n"
            "4. DO NOT present any affiliations or titles as fact unless they appear in the Verified Facts.\n"
            "5. The observation MUST explicitly list the specific domain names found in the Measured Channel Footprint to provide visible evidence of the claim.\n"
            "6. ONE-PAGE BREVITY: Keep observation, strategic_impact, and recommendation strictly under 140 characters each so the entire diagnostic fits on a single page.\n\n"
            "Synthesize exactly THREE strategic presence gaps explaining how this executive underrepresents their market authority:\n"
            "Gap 1: Authority Under-Indexing (dimension: 'AUTHORITY_UNDER_INDEXING')\n"
            "Gap 2: Channel Diversity Deficit (dimension: 'CHANNEL_DIVERSITY_DEFICIT')\n"
            "Gap 3: Narrative Fragmentation (dimension: 'NARRATIVE_FRAGMENTATION')\n\n"
            "Return JSON with key 'gaps', containing an array of 3 items, each with:\n"
            "- 'rank': integer (1, 2, or 3)\n"
            "- 'dimension': string matching one of the 3 dimensions above\n"
            "- 'title': short punchy title\n"
            "- 'observation': specific factual observation grounded in evidence\n"
            "- 'strategic_impact': commercial or strategic impact\n"
            "- 'recommendation': Growpido's actionable recommendation"
        )

        try:
            data = self.client.chat_completion_json(
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1000,
                temperature=0.2
            )
            items = data.get("gaps", [])
            gaps = []
            for item in items[:3]:
                dim_str = item.get("dimension", GapDimension.AUTHORITY_UNDER_INDEXING.value)
                try:
                    dimension = GapDimension(dim_str)
                except ValueError:
                    dimension = GapDimension.AUTHORITY_UNDER_INDEXING

                gap = StrategicGap(
                    prospect_id=prospect_id,
                    rank=item.get("rank", len(gaps) + 1),
                    dimension=dimension,
                    title=item.get("title", ""),
                    observation=item.get("observation", ""),
                    strategic_impact=item.get("strategic_impact", ""),
                    recommendation=item.get("recommendation", "")
                )
                gaps.append(gap)

            if len(gaps) == 3:
                return gaps
            return default_gaps
        except Exception:
            return default_gaps
