import sys, unittest
sys.path.insert(0, "/home/runner/work/ai-world-core/ai-world-core/vault/specialists/structured_log_sanitizer_1788551783")
from service import EngineService

class TestSanity(unittest.TestCase):
    def test_run(self):
        engine = EngineService()
        res = engine.execute("Sample test input data with test@domain.com")
        self.assertIsInstance(res, dict)
        self.assertIn("status", res)

if __name__ == "__main__":
    unittest.main()
