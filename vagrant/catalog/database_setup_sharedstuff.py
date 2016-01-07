import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from sqlalchemy.orm import backref

Base = declarative_base()


class User(Base):
    __tablename__ = 'user'

    user_id = Column(Integer, primary_key=True)
    email_id = Column(String(250), nullable=False)
    name = Column(String(250), nullable=True)


class Product(Base):
    __tablename__ = 'product'

    product_id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    description = Column(String(250))
    category = Column(String(250))
    identifier = Column(String(250))
    identifier_value = Column(String(250))
    is_active = Column(Boolean, default=True, nullable=False)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
           'product_id': self.product_id,
           'name': self.name,
           'description': self.description,
           'category': self.category,
           'identifier': self.identifier,
           'identifier_value': self.identifier_value,
           'is_active': self.is_active,
           }


class Listing(Base):
    __tablename__ = 'listing'

    listing_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.user_id'), nullable=False)
    product_id = Column(Integer, ForeignKey('product.product_id'), nullable=False)
    deposit = Column(String(8))
    max_days = Column(Integer)
    is_available = Column(Boolean, default=True, nullable=False)
    user = relationship(User)
    product = relationship(Product, cascade="all,delete")

    # serialize function to send JSON objects in a serializable format
    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
           'listing_id': self.listing_id,
           'user_id': self.user_id,
           'product_id': self.product_id,
           'deposit': self.deposit,
           'max_days': self.max_days,
           'is_available': self.is_available,
           }

engine = create_engine('sqlite:///sharedstuff.db')
Base.metadata.create_all(engine)
