import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey, Integer, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class Subscription(Base):
    __tablename__ = "subscriptions"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False, unique=True)
    plan_tier = Column(String(50), default="FREE") # FREE, BASIC, PROFESSIONAL, ENTERPRISE
    status = Column(String(50), default="active") # active, trialing, past_due, canceled
    provider = Column(String(50), nullable=True) # stripe, razorpay
    provider_subscription_id = Column(String(255), nullable=True)
    current_period_end = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    organization = relationship("Organization", back_populates="subscription")

class PaymentLog(Base):
    __tablename__ = "payment_logs"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    amount = Column(Integer, nullable=False) # In lowest denomination (cents/paise)
    currency = Column(String(10), default="INR")
    status = Column(String(50), nullable=False)
    transaction_id = Column(String(255), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
