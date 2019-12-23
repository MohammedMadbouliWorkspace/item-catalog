import sys
from sqlalchemy import Column, ForeignKey, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

# User table
class User(Base):
    __tablename__ = "user"

    id = Column(
        Integer,
        primary_key=True
    )

    username = Column(
        String(32),
        index=True,
        nullable=False
    )

    name = Column(
        String(64),
        nullable=False
    )

    email = Column(
        String,
        nullable=False
    )

    image = Column(
        String
    )


# Category table
class Category(Base):
    __tablename__ = "category"

    id = Column(
        Integer,
        primary_key=True
    )

    user_id = Column(
        Integer,
        ForeignKey('user.id')
    )

    name = Column(
        String(64),
        index=True,
        nullable=False
    )


# Item table
class Item(Base):
    __tablename__ = "item"

    id = Column(
        Integer,
        primary_key=True
    )

    user_id = Column(
        Integer,
        ForeignKey('user.id')
    )

    category_id = Column(
        Integer,
        ForeignKey('category.id')
    )

    category_name = Column(
        String,
        ForeignKey('category.name')
    )

    name = Column(
        String(64),
        index=True,
        nullable=False
    )

    description = Column(
        String,
        nullable=False
    )

    image = Column(
        String
    )


engine = create_engine('sqlite:///catalog.db')

Base.metadata.create_all(engine)