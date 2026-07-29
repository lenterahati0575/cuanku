from fpdf import FPDF
from datetime import datetime

class ReportGenerator:
    def __init__(self, db):
        self.db = db
    
    def generate(self, tickers=None, output_path="report.pdf") -> str:
        """Generate PDF report"""
        try:
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=16)
            pdf.cell(200, 10, txt="IDX Screener Report", ln=True, align='C')
            pdf.ln(10)
            
            pdf.set_font("Arial", size=12)
            pdf.cell(200, 10, txt=f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", ln=True)
            pdf.ln(10)
            
            # Market Overview
            pdf.set_font("Arial", size=14)
            pdf.cell(200, 10, txt="Market Overview", ln=True)
            pdf.ln(5)
            
            scores = self.db.get_latest_scores(min_score=0, limit=50)
            if not scores.empty:
                pdf.set_font("Arial", size=10)
                pdf.cell(200, 10, txt=f"Total Stocks Analyzed: {len(scores)}", ln=True)
                pdf.cell(200, 10, txt=f"Average Score: {scores['composite_score'].mean():.1f}", ln=True)
            
            pdf.output(output_path)
            return output_path
        except Exception as e:
            raise Exception(f"Error generating PDF: {e}")
