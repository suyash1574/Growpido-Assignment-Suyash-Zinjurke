from typing import List
from src.storage.models import Claim, ClaimStatus

class RefusalEngine:
    REFUSAL_REASONS = {
        "REF-01": "No Tier-1 primary source (government registry, regulatory filing, or official corporate domain) corroborated this assertion.",
        "REF-02": "Unresolved contradiction detected across authoritative public sources regarding dates, titles, or metrics.",
        "REF-03": "Subjective marketing puffery or uncertified accolade lacking institutional proof.",
        "REF-04": "Initial primary check succeeded, but independent secondary corroboration failed or was unreachable.",
        "REF-05": "Stale public record superseded by subsequent regulatory updates."
    }

    @classmethod
    def process(cls, claims: List[Claim]) -> List[Claim]:
        """
        Quarantines claims that cannot achieve VERIFIED status.
        Attaches standardized refusal codes and causal explanations pursuant to Rule BR-R01.
        """
        for claim in claims:
            if claim.status == ClaimStatus.UNVERIFIED:
                if not claim.check1_passed:
                    claim.refusal_code = "REF-01"
                    claim.refusal_reason = (
                        f"{cls.REFUSAL_REASONS['REF-01']} While secondary aggregators or blogs mentioned this claim, "
                        "no audited record or regulatory filing exists to substantiate it."
                    )
                elif not claim.check2_passed:
                    claim.refusal_code = "REF-04"
                    claim.refusal_reason = cls.REFUSAL_REASONS["REF-04"]
            elif claim.status == ClaimStatus.PARTIALLY_VERIFIED and claim.contradiction_detected:
                claim.status = ClaimStatus.UNVERIFIED
                claim.refusal_code = "REF-02"
                claim.refusal_reason = f"{cls.REFUSAL_REASONS['REF-02']} Details: {claim.contradiction_details or 'Discrepancy found across public sources.'}"

            # Guarantee any claim with an active refusal code is formally UNVERIFIED (quarantined)
            if claim.refusal_code:
                claim.status = ClaimStatus.UNVERIFIED

        return claims
