import sys, unittest
sys.path.insert(0, "C:/Users/HP/Desktop/VASTUDA/vault/autonomous_assets/local-rate-limit-simulator")
from service import EngineService

class TestAsset(unittest.TestCase):
    def test_run(self):
        engine = EngineService()
        result = engine.execute("sample_data_stream, genesis_verify")
        self.assertIsInstance(result, dict)
        self.assertIn("status", result)

if __name__ == "__main__":
    unittest.main()
