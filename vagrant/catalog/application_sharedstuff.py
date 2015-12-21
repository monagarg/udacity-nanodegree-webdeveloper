from flask import Flask, render_template, request, redirect, url_for
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup_sharedstuff import User, Base, Product, Listing

app = Flask(__name__)

engine = create_engine('sqlite:///sharedstuff.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

@app.route('/')
@app.route('/alllistings/')
def allListings():
	products = []
	listings = session.query(Listing).filter_by(is_available = True).all()
	for listing in listings:
		products.append(session.query(Product).filter_by(product_id = listing.product_id).one())
	return render_template('alllistings.html',products = products)

# Task 3: Create a route for deleteMenuItem function here

@app.route('/allusers/')
def allUsers():
	users = []
	all_users = session.query(User).all()
	for user in all_users:
		users.append(session.query(User).filter_by(user_id = user.user_id).one())
	return render_template('allusers.html',users = users)

# Task 3: Create a route for deleteMenuItem function here

@app.route('/products/<int:product_id>/')
def productDetails(product_id):
	product = session.query(Product).filter_by(product_id = product_id).one()
	return render_template('productdetails.html',product = product)

# Task 3: Create a route for deleteMenuItem function here

@app.route('/products/<int:user_id>/new', methods=['GET', 'POST'])
def newListing(user_id):
	if request.method == 'POST':
		newProduct = Product(name = request.form['name'], description = request.form['description'], category = request.form['category'], identifier = request.form['identifier'], identifier_value = request.form['identifier_value'])
		newProductListing = Listing(deposit = request.form['deposit'], max_days = request.form['max_days'], user_id = user_id, product = newProduct)
		session.add(newProduct)
		session.add(newProductListing)
		session.commit()
		return redirect(url_for('allListings'))
	else:
		return render_template('newlisting.html',user_id = user_id)

# Task 3: Create a route for deleteMenuItem function here

@app.route('/products/<int:product_id>/edit', methods=['GET', 'POST'])
def editListing(product_id):
	editedProduct = session.query(Product).filter_by(product_id=product_id).one()
	editedList = session.query(Listing).filter_by(product_id=product_id).one()
	if request.method == 'POST':
		if request.form:
			editedProduct.name = request.form['name']
			editedProduct.description = request.form['description']
			editedProduct.category = request.form['category']
			editedProduct.identifier = request.form['identifier']
			editedProduct.identifier_value = request.form['identifier_value']
			editedList.deposit = request.form['deposit']
			editedList.max_days = request.form['max_days']
		session.add(editedProduct)
		session.commit()
		return redirect(url_for('allListings'))
	else:
		return render_template('editlisting.html',product_id=product_id, product=editedProduct, listing=editedList)

# Task 3: Create a route for deleteMenuItem function here

@app.route('/products/<int:product_id>/delete', methods=['GET','POST'])
def deleteProduct(product_id):
	deletedProduct = session.query(Product).filter_by(product_id=product_id).one()
	deletedList = session.query(Listing).filter_by(product_id=product_id).one()
	if request.method == 'POST':
		if deletedProduct.product_id:
			deletedProduct.is_active = False
			deletedList.is_available = False
		session.add(deletedProduct)
		session.add(deletedList)
		session.commit()
		return redirect(url_for('allListings'))
	else:
		return render_template('deletelisting.html',product_id=product_id,product=deletedProduct, listing=deletedList)


if __name__ == '__main__':
	app.debug = True
	app.run(host='0.0.0.0', port=5000)