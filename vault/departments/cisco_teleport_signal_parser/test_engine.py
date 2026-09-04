import sys, unittest
sys.path.insert(0, "C:/Users/HP/Desktop/VASTUDA/vault/departments/cisco_teleport_signal_parser")
from engine import EngineService

class TestAudit(unittest.TestCase):
    def test_run(self):
        eng = EngineService()
        out = eng.execute("Sample_Genesis_Telemetry_Input")
        self.assertIsInstance(out, dict)

if __name__ == "__main__":
    unittest.main()
