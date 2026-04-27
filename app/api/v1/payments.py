from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.v1.error_handlers import handle_integrity_error
from app.core.db import get_db
from app.models.enums import OrderStatus, PaymentStatus
from app.models.payment import Payment
from app.models.sales_order import SalesOrder
from app.schemas.payment import PaymentCreate, PaymentRead
from app.services.orders_service import get_order_or_404
from app.services.payments_service import (
    get_payment_or_404, 
    get_payments_by_order_id,
    to_payment_read,
    generate_payment_number
)

router = APIRouter(tags=["payments"])


@router.get("/payments", response_model=list[PaymentRead])
def get_payments(
    order_id: int | None = Query(default=None),
    db: Session = Depends(get_db),
):
    stmt = select(Payment)

    if order_id is not None:
        stmt = stmt.where(Payment.order_id == order_id)

    stmt = stmt.order_by(Payment.payment_id)

    payments = db.execute(stmt).scalars().all()
    return [to_payment_read(payment) for payment in payments]


@router.get("/payments/{payment_id}", response_model=PaymentRead)
def get_payment(payment_id: int, db: Session = Depends(get_db)):
    payment = get_payment_or_404(payment_id, db)
    return to_payment_read(payment)


@router.post("/orders/{order_id}/payments", response_model=PaymentRead)
def create_payment_for_order(
    order_id: int,
    payload: PaymentCreate,
    db: Session = Depends(get_db),
):
    order = get_order_or_404(order_id, db)

    if order.order_status not in {
        OrderStatus.NEW.value,
        OrderStatus.RESERVED.value,
        OrderStatus.RELEASED.value,
    }:
        raise HTTPException(
            status_code=400,
            detail="Payments can only be created for orders in NEW, RESERVED, or RELEASED status.",
        )

    existing_payments = get_payments_by_order_id(order.order_id, db)

    has_blocking_payment = any(
        payment.payment_status in {
            PaymentStatus.PENDING.value,
            PaymentStatus.PAID.value,
        }
        for payment in existing_payments
    )
    if has_blocking_payment:
        raise HTTPException(
            status_code=400,
            detail="Cannot create a new payment while the order has an active PENDING or PAID payment.",
        )

    attempt_no = len(existing_payments) + 1

    payment = Payment(
        payment_number=generate_payment_number(order.order_id, attempt_no),
        order_id=order.order_id,
        payment_status=PaymentStatus.PENDING.value,
        payment_method=payload.payment_method,
        amount=order.order_total_amount,
        paid_datetime=None,
    )
    db.add(payment)

    try:
        db.commit()
    except IntegrityError as exc:
        handle_integrity_error(db, exc)

    db.refresh(payment)
    return to_payment_read(payment)


@router.post("/payments/{payment_id}/complete", response_model=PaymentRead)
def complete_payment(
    payment_id: int,
    db: Session = Depends(get_db),
):
    payment = get_payment_or_404(payment_id, db)

    if payment.payment_status != PaymentStatus.PENDING.value:
        raise HTTPException(
            status_code=400,
            detail="Only payments in PENDING status can be completed.",
        )

    payment.payment_status = PaymentStatus.PAID.value
    payment.paid_datetime = datetime.now(timezone.utc)

    db.commit()
    db.refresh(payment)

    return to_payment_read(payment)


@router.post("/payments/{payment_id}/fail", response_model=PaymentRead)
def fail_payment(
    payment_id: int,
    db: Session = Depends(get_db),
):
    payment = get_payment_or_404(payment_id, db)

    if payment.payment_status != PaymentStatus.PENDING.value:
        raise HTTPException(
            status_code=400,
            detail="Only payments in PENDING status can be failed.",
        )

    payment.payment_status = PaymentStatus.FAILED.value

    db.commit()
    db.refresh(payment)

    return to_payment_read(payment)