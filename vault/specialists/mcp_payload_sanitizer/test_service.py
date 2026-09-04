import sys, unittest
sys.path.insert(0, "C:/Users/HP/Desktop/VASTUDA/vault/specialists/mcp_payload_sanitizer")
from service import EngineService

class TestSanity(unittest.TestCase):
    def test_run(self):
        engine = EngineService()
        res = engine.execute("Sample test input data with test@domain.com")
        self.assertIsInstance(res, dict)
        self.assertIn("status", res)

if __name__ == "__main__":
    unittest.main()
