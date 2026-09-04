import sys, unittest
sys.path.insert(0, "C:/Users/HP/Desktop/VASTUDA/vault/autonomous_assets/maze_prototype_feedback_engine")
from service import EngineService

class TestAsset(unittest.TestCase):
    def test_run(self):
        engine = EngineService()
        result = engine.execute("sample_data_stream, genesis_verify")
        self.assertIsInstance(result, dict)
        self.assertIn("status", result)

if __name__ == "__main__":
    unittest.main()
