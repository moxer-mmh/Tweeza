from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from datetime import datetime

from app.db import Beneficiary, AssistanceRecord, User, Event


class BeneficiaryService:
    def __init__(self, db: Session):
        self.db = db

    def create_beneficiary(self, user_id: int, needs: str) -> Beneficiary:
        """Create a beneficiary profile for a user."""
        # Check if user exists
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError("User not found")

        # Check if beneficiary already exists
        existing = (
            self.db.query(Beneficiary).filter(Beneficiary.user_id == user_id).first()
        )
        if existing:
            raise ValueError("Beneficiary profile already exists for this user")

        # Create beneficiary profile
        beneficiary = Beneficiary(user_id=user_id, needs=needs)

        self.db.add(beneficiary)
        self.db.commit()
        self.db.refresh(beneficiary)
        return beneficiary

    def get_beneficiary_by_id(self, beneficiary_id: int) -> Optional[Beneficiary]:
        """Get beneficiary profile by ID."""
        return (
            self.db.query(Beneficiary)
            .options(
                joinedload(Beneficiary.user), joinedload(Beneficiary.assistance_history)
            )
            .filter(Beneficiary.id == beneficiary_id)
            .first()
        )

    def get_beneficiary_by_user_id(self, user_id: int) -> Optional[Beneficiary]:
        """Get beneficiary profile by user ID."""
        return (
            self.db.query(Beneficiary)
            .options(
                joinedload(Beneficiary.user), joinedload(Beneficiary.assistance_history)
            )
            .filter(Beneficiary.user_id == user_id)
            .first()
        )

    def update_needs(self, beneficiary_id: int, needs: str) -> Optional[Beneficiary]:
        """Update a beneficiary's needs description."""
        beneficiary = (
            self.db.query(Beneficiary).filter(Beneficiary.id == beneficiary_id).first()
        )
        if not beneficiary:
            return None

        beneficiary.needs = needs
        self.db.commit()
        self.db.refresh(beneficiary)
        return beneficiary

    def record_assistance(
        self, beneficiary_id: int, event_id: int, assistance_type: str
    ) -> AssistanceRecord:
        """Record assistance provided to a beneficiary."""
        # Verify beneficiary exists
        beneficiary = (
            self.db.query(Beneficiary).filter(Beneficiary.id == beneficiary_id).first()
        )
        if not beneficiary:
            raise ValueError("Beneficiary not found")

        # Verify event exists
        event = self.db.query(Event).filter(Event.id == event_id).first()
        if not event:
            raise ValueError("Event not found")

        # Create assistance record
        record = AssistanceRecord(
            beneficiary_id=beneficiary_id,
            event_id=event_id,
            assistance_type=assistance_type,
            assistance_date=datetime.utcnow(),
        )

        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record

    def get_assistance_history(self, beneficiary_id: int) -> List[AssistanceRecord]:
        """Get assistance history for a beneficiary."""
        return (
            self.db.query(AssistanceRecord)
            .filter(AssistanceRecord.beneficiary_id == beneficiary_id)
            .order_by(AssistanceRecord.assistance_date.desc())
            .all()
        )
