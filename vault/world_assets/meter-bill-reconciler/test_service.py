import sys, unittest
sys.path.insert(0, "C:/Users/HP/Desktop/VASTUDA/vault/world_assets/meter-bill-reconciler")
from service import EngineService

class TestEngine(unittest.TestCase):
    def test_run(self):
        engine = EngineService()
        res = engine.execute("sample_data_stream")
        self.assertIsInstance(res, dict)

if __name__ == "__main__":
    unittest.main()
