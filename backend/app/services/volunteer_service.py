from typing import List, Optional
from sqlalchemy.orm import Session, joinedload

from app.db import Volunteer, VolunteerSkill, Skill, User
from app.schemas import VolunteerSkillBase


class VolunteerService:
    def __init__(self, db: Session):
        self.db = db

    def get_volunteer_by_id(self, volunteer_id: int) -> Optional[Volunteer]:
        """Get volunteer by ID."""
        return self.db.query(Volunteer).filter(Volunteer.id == volunteer_id).first()

    def get_volunteer_by_user_id(self, user_id: int) -> Optional[Volunteer]:
        """Get volunteer profile by user ID."""
        return self.db.query(Volunteer).filter(Volunteer.user_id == user_id).first()

    def create_volunteer_profile(self, user_id: int) -> Volunteer:
        """Create volunteer profile for a user."""
        # Check if volunteer profile already exists
        existing_profile = self.get_volunteer_by_user_id(user_id)
        if existing_profile:
            return existing_profile

        # Check if user exists
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError("User not found")

        # Create volunteer profile
        volunteer = Volunteer(user_id=user_id)
        self.db.add(volunteer)
        self.db.commit()
        self.db.refresh(volunteer)
        return volunteer

    def add_skill(self, volunteer_id: int, skill_id: int, level: int) -> VolunteerSkill:
        """Add or update a skill for a volunteer."""
        # Check if volunteer exists
        volunteer = self.get_volunteer_by_id(volunteer_id)
        if not volunteer:
            raise ValueError("Volunteer not found")

        # Check if skill exists
        skill = self.db.query(Skill).filter(Skill.id == skill_id).first()
        if not skill:
            raise ValueError("Skill not found")

        # Check if the volunteer already has this skill
        volunteer_skill = (
            self.db.query(VolunteerSkill)
            .filter(
                VolunteerSkill.volunteer_id == volunteer_id,
                VolunteerSkill.skill_id == skill_id,
            )
            .first()
        )

        if volunteer_skill:
            # Update existing skill level
            volunteer_skill.level = level
        else:
            # Add new skill
            volunteer_skill = VolunteerSkill(
                volunteer_id=volunteer_id, skill_id=skill_id, level=level
            )
            self.db.add(volunteer_skill)

        self.db.commit()
        self.db.refresh(volunteer_skill)
        return volunteer_skill

    def remove_skill(self, volunteer_id: int, skill_id: int) -> bool:
        """Remove a skill from a volunteer."""
        volunteer_skill = (
            self.db.query(VolunteerSkill)
            .filter(
                VolunteerSkill.volunteer_id == volunteer_id,
                VolunteerSkill.skill_id == skill_id,
            )
            .first()
        )

        if not volunteer_skill:
            return False

        self.db.delete(volunteer_skill)
        self.db.commit()
        return True

    def get_volunteers_with_skill(
        self, skill_id: int, min_level: int = 1
    ) -> List[Volunteer]:
        """Find volunteers with a specific skill and minimum level."""
        return (
            self.db.query(Volunteer)
            .join(VolunteerSkill, Volunteer.id == VolunteerSkill.volunteer_id)
            .filter(
                VolunteerSkill.skill_id == skill_id, VolunteerSkill.level >= min_level
            )
            .all()
        )
