class BidStrategyBase:
    def __init__(self, min_bid_multiplier=1, max_bid_multiplier=1):
        self.min_bid_multiplier = min_bid_multiplier
        self.max_bid_multiplier = max_bid_multiplier

    async def bid(self, guid, mask, verdicts, confidences, metadatas, min_allowed_bid, chain):
        """Override this to implement custom bid calculation logic

        Args:
            guid (str): GUID of the bounty under analysis
            mask (list[bool]): mask for the from scanning the bounty files
            verdicts (list[bool]): scan verdicts from scanning the bounty files
            confidences (list[float]): Measure of confidence of verdict per artifact ranging from 0.0 to 1.0
            metadatas (list[str]): metadata blurbs from scanning the bounty files
            min_allowed_bid (int): Minimum bid value as specified by the contract
            chain (str): Chain we are operating on

        Returns:
            int: Amount of NCT to bid in base NCT units (10 ^ -18)
        """
        min_bid = max(min_allowed_bid * self.min_bid_multiplier, min_allowed_bid)
        max_bid = max(min_allowed_bid * self.max_bid_multiplier, min_allowed_bid)

        asserted_confidences = [c for b, c in zip(mask, confidences) if b]
        avg_confidence = sum(asserted_confidences) / len(asserted_confidences) if asserted_confidences else 0
        bid = int(min_bid + ((max_bid - min_bid) * avg_confidence))

        # Clamp bid between min_bid and max_bid
        return max(min_bid, min(bid, max_bid))
