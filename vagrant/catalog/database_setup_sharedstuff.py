import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()

class User(Base):
    __tablename__ = 'user'
   
    user_id = Column(Integer, primary_key=True)
    email_id = Column(String(250), nullable=True)
    name = Column(String(250), nullable=False)

class Product(Base):
    __tablename__ = 'product'

    product_id = Column(Integer, primary_key = True)
    name = Column(String(250), nullable = False)
    description = Column(String(250),nullable=False)
    category = Column(String(250),nullable=False)
    identifier = Column(String(250),nullable=False)
    identifier_value = Column(String(250),nullable=False)
    is_active = Column(String(2))

class Listing(Base):
    __tablename__ = 'listing'

    listing_id = Column(Integer, primary_key = True)
    user_id = Column(Integer, ForeignKey('user.user_id'),nullable=True)
    product_id = Column(Integer, ForeignKey('product.product_id'),nullable=True)
    deposit = Column(String(8))
    max_days = Column(Integer)
    is_rented = Column(String(2))
    user = relationship(User)
    product = relationship(Product)

engine = create_engine('sqlite:///sharedstuff.db')
Base.metadata.create_all(engine)