from datetime import datetime
from typing import Optional, List
from sqlalchemy import String, Integer, TIMESTAMP, ForeignKey, BigInteger
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Habit(Base):
    __tablename__ = "habits"

    id: Mapped[int] = mapped_column(BigInteger().with_variant(Integer, "sqlite"), primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(150))
    description: Mapped[Optional[str]] = mapped_column(String(400))
    periodicity: Mapped[int] = mapped_column(Integer)
    creation_date: Mapped[datetime] = mapped_column(TIMESTAMP, default=datetime.utcnow)

    check_offs: Mapped[List["CheckOff"]] = relationship(
        back_populates="habit"
    )

    def __repr__(self):
        return f"<Habit {self.id!r} - {self.name!r}>"


class CheckOff(Base):
    __tablename__ = 'check_offs'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    habit_id: Mapped[int] = mapped_column(ForeignKey("habits.id"))
    date_time: Mapped[datetime] = mapped_column(TIMESTAMP, default=datetime.utcnow)

    habit: Mapped["Habit"] = relationship("Habit", back_populates="check_offs")

    def __repr__(self):
        return f"<CheckOff(id={self.id}, date_time={self.date_time})>"
