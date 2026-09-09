import sys
import os
import json
import time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from scripts.pflc_5_3_intensive_runner import run_intensive_mode
from execution.pipeline import ExecutionPipeline
from risk.risk_guard import RiskGuard
from economics.profit_calculator import ProfitCalculator
from risk.auditor import IndependentAuditor

class PFLC54SaturationTester:
    def __init__(self):
        self.pipeline = ExecutionPipeline(RiskGuard(), ProfitCalculator())
        self.auditor = IndependentAuditor(target_dir=os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
        
    def run_saturation(self):
        print("Starting PFLC-5.4 Saturation Testing (Base + Spatial Priority)...")
        # For this test, we execute the runner 1 time which internally loops configurations
        run_intensive_mode()
        
        print("\nPipeline execution complete. Running Independent Auditor...")
        self.auditor.audit()
        print("Saturation Testing Complete. All logs saved in PFLC_5.4_Reports.")

if __name__ == "__main__":
    tester = PFLC54SaturationTester()
    tester.run_saturation()
