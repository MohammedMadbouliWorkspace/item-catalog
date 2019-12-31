import random
import string
import sys
from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    String,
    create_engine,
    DateTime,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from itsdangerous import (
    TimedJSONWebSignatureSerializer as Serializer,
    BadSignature,
    SignatureExpired,
)

Base = declarative_base()
secret_key = "".join(
    random.choice(string.ascii_uppercase + string.digits) for i in xrange(32)
)

# User table


class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True)

    username = Column(String(32), index=True, nullable=False)

    name = Column(String(64), nullable=False)

    email = Column(String, nullable=False)

    image = Column(String)

    def generate_auth_token(self, expiration=3600):
        s = Serializer(secret_key, expires_in=expiration)
        return s.dumps({"id": self.id})

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(secret_key)
        try:
            data = s.loads(token)

        except SignatureExpired:
            return None

        except BadSignature:
            return None

        user_id = data["id"]
        return user_id

    @property
    def serialize(self):
        return {
            "id": self.id,
            "username": self.username,
            "name": self.name,
            "image": self.image,
        }


class Colors(Base):
    __tablename__ = "colors"

    id = Column(Integer, primary_key=True)

    colors = Column(String(13), nullable=False)

    @property
    def serialize(self):
        return {"id": self.id, "colors": self.colors}


# Category table
class Category(Base):
    __tablename__ = "category"

    id = Column(Integer, primary_key=True)

    user_id = Column(Integer, ForeignKey("user.id"))

    name = Column(String(64), index=True, nullable=False)

    colors_id = Column(Integer, ForeignKey("colors.id"))

    user = relationship(User)

    colors = relationship(Colors)

    @property
    def serialize(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "name": self.name,
            "user": self.user.serialize,
            "colors": self.colors.serialize,
        }

    @property
    def mini_serialize(self):
        return {"id": self.id, "user_id": self.user_id, "name": self.name}


# Item table
class Item(Base):
    __tablename__ = "item"

    id = Column(Integer, primary_key=True)

    user_id = Column(Integer, ForeignKey("user.id"))

    category_id = Column(Integer, ForeignKey("category.id"))

    name = Column(String(64), index=True, nullable=False)

    description = Column(String, nullable=False)

    image = Column(String)

    creation_date = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship(User)

    category = relationship(Category)

    @property
    def serialize(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "category_id": self.category_id,
            "name": self.name,
            "description": self.description,
            "image": self.image,
            "user": self.user.serialize,
            "category": self.category.mini_serialize,
        }

    @property
    def mini_serialize(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "category_id": self.category_id,
            "name": self.name,
            "description": self.description,
            "image": self.image,
        }


engine = create_engine("sqlite:///catalog.db")

Base.metadata.create_all(engine)
