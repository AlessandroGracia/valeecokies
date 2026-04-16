from app.core.database import SessionLocal
from app.services.cash_register_service import CashRegisterService

db = SessionLocal()
summary = CashRegisterService.get_cash_register_summary(db)
print("Total sales count:", summary.total_sales_count)
print("Total sales amt:", summary.total_sales_amount)
db.close()
