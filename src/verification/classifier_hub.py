from src.storage.models import Claim, ClaimStatus

class ClassifierHub:
    @staticmethod
    def classify(claim: Claim) -> ClaimStatus:
        """
        Determines verified status based on two-stage checks and contradiction rules:
        - VERIFIED: Tier-1 Primary Entailment passed (Check 1) AND Independent Corroboration passed (Check 2) AND No Contradiction.
        - PARTIALLY_VERIFIED: Check 1 passed but Check 2 uncorroborated, OR contradiction detected between sources.
        - UNVERIFIED: Check 1 failed (no primary Tier-1 evidence).
        """
        if claim.contradiction_detected:
            return ClaimStatus.PARTIALLY_VERIFIED

        if claim.check1_passed and claim.check2_passed:
            return ClaimStatus.VERIFIED

        if claim.check1_passed and not claim.check2_passed:
            return ClaimStatus.PARTIALLY_VERIFIED

        # If primary Tier-1 was missing or failed, but independent Tier-2 reputable press corroborated it
        if not claim.check1_passed and claim.check2_passed:
            return ClaimStatus.PARTIALLY_VERIFIED

        return ClaimStatus.UNVERIFIED
