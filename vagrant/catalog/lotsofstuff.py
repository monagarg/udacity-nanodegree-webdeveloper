from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup_sharedstuff import User, Base, Product, Listing

engine = create_engine('sqlite:///sharedstuff.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()


# Users
user1 = User(email_id="garg.mona@gmail.com", name="Mona Garg")

session.add(user1)
session.commit()

user2 = User(email_id="aniketbhatt3@gmail.com", name="Aniket Bhatt")

session.add(user2)
session.commit()

# Products
product1 = Product(name="The WebApplication Hacker's Handbook", description="The Web Application Hacker's Handbook second addition", category="Books", identifier="ISBN", identifier_value="11122223333")

session.add(product1)
session.commit()


product2 = Product(name="THe Hacker Playbook", description="The Hacker Playbook", category="Books", identifier="ISBN", identifier_value="22223333444")

session.add(product2)
session.commit()

product3 = Product(name="Security +", description="Security +", category="Books", identifier="ISBN", identifier_value="33334444555")

session.add(product3)
session.commit()

product4 = Product(name="Network Security", description="Network Security", category="Books", identifier="ISBN", identifier_value="44445555666")

session.add(product4)
session.commit()

product5 = Product(name="Applied Cryptography", description="Applied Cryptography", category="Books", identifier="ISBN", identifier_value="55556666777")

session.add(product5)
session.commit()

product6 = Product(name="Python Programming", description="Python Programming", category="Books", identifier="ISBN", identifier_value="66667777888")

session.add(product6)
session.commit()

# Listings
listing1 = Listing(deposit="1.99", max_days="20", user=user1, product=product1)

session.add(listing1)
session.commit()

listing2 = Listing(deposit="2.99", max_days="30", user=user1, product=product2)

session.add(listing2)
session.commit()

listing3 = Listing(deposit="2.49", max_days="40", user=user1, product=product3)

session.add(listing3)
session.commit()

listing4 = Listing(deposit="1.59", max_days="25", user=user2, product=product4)

session.add(listing4)
session.commit()

listing5 = Listing(deposit="2.99", max_days="35", user=user2, product=product5)

session.add(listing5)
session.commit()

listing6 = Listing(deposit="3.99", max_days="45", user=user2, product=product6)

session.add(listing6)
session.commit()

print "added users, products, and listings!"
