import csv
import os
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from app.database.db_session import SessionLocal
from app.database.models import AuditLog

class AuditExportService:
    @staticmethod
    def export_to_csv(file_path):
        db = SessionLocal()
        try:
            logs = db.query(AuditLog).all()
            with open(file_path, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['ID', 'Timestamp', 'Action', 'Outcome', 'Details'])
                for log in logs:
                    writer.writerow([log.id, log.timestamp, log.action_type, log.outcome.value, log.details])
            return True
        except Exception:
            return False
        finally:
            db.close()

    @staticmethod
    def export_to_pdf(file_path):
        db = SessionLocal()
        try:
            logs = db.query(AuditLog).all()
            c = canvas.Canvas(file_path, pagesize=letter)
            width, height = letter

            c.setFont("Helvetica-Bold", 16)
            c.drawString(50, height - 50, "MPM Audit Log Report")
            c.setFont("Helvetica", 10)
            c.drawString(50, height - 70, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

            y = height - 100
            for log in logs:
                if y < 50:
                    c.showPage()
                    y = height - 50

                text = f"[{log.timestamp}] {log.action_type} - {log.outcome.value}"
                c.drawString(50, y, text)
                y -= 15
                details = str(log.details)[:100]
                c.drawString(70, y, f"Details: {details}")
                y -= 25

            c.save()
            return True
        except Exception:
            return False
        finally:
            db.close()
