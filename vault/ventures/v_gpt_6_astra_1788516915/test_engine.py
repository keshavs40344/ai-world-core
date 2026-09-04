import sys
import unittest
sys.path.insert(0, "C:/Users/HP/Desktop/VASTUDA/vault/ventures/v_gpt_6_astra_1788516915")
from product_engine import EngineService

class TestEngineService(unittest.TestCase):
    def setUp(self):
        self.engine = EngineService()

    def test_nominal_execution(self):
        result = self.engine.process_data("active_traffic_input")
        self.assertEqual(result["status"], "PROCESSED")
        self.assertEqual(len(result["sha256"]), 64)

    def test_empty_input_exception(self):
        with self.assertRaises(ValueError):
            self.engine.process_data("")

    def test_sanitization(self):
        dirty = "Test" + chr(0) + "Payload"
        res = self.engine.process_data(dirty)
        self.assertEqual(res["length"], 11)

if __name__ == "__main__":
    unittest.main()
