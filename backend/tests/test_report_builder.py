import unittest
from app.reports.builder import ReportBuilder

class TestReportBuilder(unittest.TestCase):
    def setUp(self):
        self.builder = ReportBuilder()

    def test_handles_empty_pipeline_payload_gracefully(self):
        """
        Ensures the extractors don't raise KeyErrors when data is missing.
        This guarantees backwards compatibility if engine schemas change.
        """
        report = self.builder.build_json_report({}, {})
        
        self.assertEqual(report.master_probability.data_points.get("final_score"), 0.0)
        self.assertEqual(report.master_probability.data_points.get("grade"), "UNKNOWN")
        self.assertEqual(report.yoga_analysis.data_points.get("active_yogas"), [])
        self.assertEqual(report.executive_summary.data_points.get("top_domains"), [])

    def test_extracts_correct_data(self):
        """
        Tests the basic happy path extraction.
        """
        mock_pipeline = {
            "master_probability": {"final_score": 85.5, "grade": "EXCELLENT"},
            "engine_outputs": {
                "natal_promise": {
                    "wealth": {"score": 90, "grade": "HIGH"},
                    "career": {"score": 50, "grade": "MODERATE"}
                },
                "dashas": {"synthesis": {"active_md": "Venus", "active_ad": "Jupiter", "active_pd": "Rahu"}},
                "yogas": {"active_yogas": [{"yoga_name": "Ruchaka Yoga", "strength": 80.0}]}
            }
        }
        
        mock_machine = {
            "native_info": {"name": "Test User"}
        }

        report = self.builder.build_json_report(mock_pipeline, mock_machine)
        
        self.assertEqual(report.client_profile.name, "Test User")
        self.assertEqual(report.master_probability.data_points["final_score"], 85.5)
        self.assertIn("Ruchaka Yoga", report.yoga_analysis.data_points["summary_map"])
        
        # Wealth should be the top domain in executive summary
        self.assertEqual(report.executive_summary.data_points["top_domains"][0], "Wealth")
        self.assertEqual(report.executive_summary.data_points["current_dasha"], "Venus-Jupiter-Rahu")
