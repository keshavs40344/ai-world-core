import sys
import unittest
sys.path.insert(0, "C:/Users/HP/Desktop/VASTUDA/vault/ventures/payload_validator_1788518987_1788518987")
from product_engine import EngineService

class TestEngine(unittest.TestCase):
    def test_run(self):
        srv = EngineService()
        res = srv.process_payload("GENESIS_TEST_PAYLOAD")
        self.assertIsNotNone(res)

if __name__ == "__main__":
    unittest.main()
