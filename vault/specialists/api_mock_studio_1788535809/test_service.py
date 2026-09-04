import sys, unittest
sys.path.insert(0, "C:/Users/HP/Desktop/VASTUDA/vault/specialists/api_mock_studio_1788535809")
from service import EngineService

class TestAudit(unittest.TestCase):
    def test_run(self):
        eng = EngineService()
        out = eng.execute("ping")
        self.assertIsInstance(out, dict)
        self.assertIn("status", out)

if __name__ == "__main__":
    unittest.main()
