import sys
import unittest
sys.path.insert(0, "/home/runner/work/ai-world-core/ai-world-core/vault/ventures/env_var_diff_engine_1788901251")
from product_engine import EngineService

class TestEngine(unittest.TestCase):
    def test_run(self):
        srv = EngineService()
        res = srv.process_payload("GENESIS_TEST_PAYLOAD")
        self.assertIsNotNone(res)

if __name__ == "__main__":
    unittest.main()
