from abc import ABC, abstractmethod

class UniversalQuoteAdapter(ABC):
    def __init__(self, fallback_manager):
        self.rpc = fallback_manager

    @abstractmethod
    def fetch_market_state(self, pair_address, token_in_address):
        pass

    @abstractmethod
    def calculate_out_given_in(self, market_state, amount_in):
        pass

class V2QuoteAdapter(UniversalQuoteAdapter):
    def fetch_market_state(self, router_address, token_in, token_out, amount_in, block_identifier='latest'):
        try:
            path = [token_in, token_out]
            quote = self.rpc.get_univ2_amounts_out(router_address, amount_in, path, block_identifier)
            quote["status"] = "VALID"
            quote["type"] = "v2"
            return quote
        except Exception as e:
            return {"error": str(e), "status": "QUOTE_FAILED"}

    def calculate_out_given_in(self, market_state, amount_in, fee_bips=30):
        # The router amountsOut already subtracts the fee natively!
        if market_state.get("status") == "QUOTE_FAILED":
            return None
            
        out = market_state.get("amountOut")
        if out is None or out <= 0:
            return None
        return out

class V3QuoteAdapter(UniversalQuoteAdapter):
    def fetch_market_state(self, quoter_address, token_in, token_out, amount_in, fee, block_identifier='latest'):
        try:
            quote = self.rpc.get_univ3_quote(quoter_address, token_in, token_out, amount_in, fee, block_identifier)
            quote["status"] = "VALID"
            return quote
        except Exception as e:
            return {"error": str(e), "status": "QUOTE_FAILED"}

    def calculate_out_given_in(self, market_state, amount_in):
        if market_state.get("status") == "QUOTE_FAILED":
            return None
        out = market_state.get("amountOut")
        if out is None or out <= 0:
            return None
        return out

class QuoteAdapterFactory:
    @staticmethod
    def get_adapter(dex_type, fallback_manager):
        if dex_type == 'v2':
            return V2QuoteAdapter(fallback_manager)
        elif dex_type == 'v3':
            return V3QuoteAdapter(fallback_manager)
        else:
            raise ValueError(f"Unknown dex type: {dex_type}")
