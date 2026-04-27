from http.client import HTTPException

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.payment import Payment
from app.models.enums import (
    PaymentStatus,
)
from app.schemas.payment import PaymentRead


def get_payment_or_404(payment_id: int, db: Session) -> Payment:
    payment = db.get(Payment, payment_id)
    if payment is None:
        raise HTTPException(status_code=404, detail="Payment not found.")
    return payment


def get_payments_by_order_id(order_id: int, db: Session) -> list[Payment]:
    stmt = (
        select(Payment)
        .where(Payment.order_id == order_id)
        .order_by(Payment.payment_id)
    )
    return db.execute(stmt).scalars().all()


def has_paid_payment_for_order(order_id: int, db: Session) -> bool:
    stmt = select(Payment).where(
        Payment.order_id == order_id,
        Payment.payment_status == PaymentStatus.PAID.value,
    )
    return db.execute(stmt).scalars().first() is not None


def to_payment_read(payment: Payment) -> PaymentRead:
    return PaymentRead.model_validate(payment)


def generate_payment_number(order_id: int, attempt_no: int) -> str:
    return f"PAY-{order_id:06d}-{attempt_no:02d}"

