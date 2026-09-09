import unittest
from unittest.mock import patch

from phantomx_core.block_pinned_rpc import BlockPinnedRpc
from phantomx_core.economic_truth import EconomicTruthError


class BlockPinnedRpcTests(unittest.TestCase):
    def test_requires_explicit_positive_block(self):
        rpc = BlockPinnedRpc(["https://example.invalid"])
        with self.assertRaises(EconomicTruthError):
            rpc.eth_call_at_block("0xabc", "0x1234", 0)

    def test_rejects_invalid_target_and_data(self):
        rpc = BlockPinnedRpc(["https://example.invalid"])
        with self.assertRaises(EconomicTruthError):
            rpc.eth_call_at_block("", "0x1234", 10)
        with self.assertRaises(EconomicTruthError):
            rpc.eth_call_at_block("0xabc", "1234", 10)

    @patch("phantomx_core.block_pinned_rpc.urllib.request.urlopen")
    def test_eth_call_uses_hex_block_tag_not_latest(self, urlopen):
        class Response:
            def __enter__(self):
                return self
            def __exit__(self, *args):
                return False
            def read(self):
                return b'{"jsonrpc":"2.0","id":1,"result":"0xfeed"}'

        urlopen.return_value = Response()
        rpc = BlockPinnedRpc(["https://rpc.test"])
        result = rpc.eth_call_at_block("0xabc", "0x1234", 42)
        self.assertEqual(result.result, "0xfeed")
        request = urlopen.call_args.args[0]
        body = request.data.decode("utf-8")
        self.assertIn('"eth_call"', body)
        self.assertIn('0x2a', body)
        self.assertNotIn('"latest"', body)

    @patch("phantomx_core.block_pinned_rpc.urllib.request.urlopen")
    def test_rpc_error_fails_closed(self, urlopen):
        class Response:
            def __enter__(self):
                return self
            def __exit__(self, *args):
                return False
            def read(self):
                return b'{"jsonrpc":"2.0","id":1,"error":{"code":-32000,"message":"boom"}}'

        urlopen.return_value = Response()
        rpc = BlockPinnedRpc(["https://rpc.test"])
        with self.assertRaises(EconomicTruthError):
            rpc.eth_call_at_block("0xabc", "0x1234", 42)


if __name__ == "__main__":
    unittest.main()
