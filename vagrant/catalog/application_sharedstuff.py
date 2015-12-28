from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup_sharedstuff import User, Base, Product, Listing
from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

app = Flask(__name__)
CLIENT_ID = json.loads(
	open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Shared Stuff Application"


# Connect to Database and create database session
engine = create_engine('sqlite:///sharedstuff.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# Create anti-forgery state token
@app.route('/login')
def showLogin():
	state = ''.join(
		random.choice(string.ascii_uppercase + string.digits) for x in xrange(32))
	login_session['state'] = state
	#return "The current session state is %s" %login_session['state']
	return render_template('login.html', STATE=state)


@app.route('/gconnect', methods=['POST'])
def gconnect():
	# Validate state token
	if request.args.get('state') != login_session['state']:
		response = make_response(json.dumps('Invalid state parameter.'), 401)
		response.headers['Content-Type'] = 'application/json'
		return response
	# Obtain authorization code
	code = request.data

	try:
		# Upgrade the authorization code into a credentials object
		oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
		oauth_flow.redirect_uri = 'postmessage'
		credentials = oauth_flow.step2_exchange(code)
	except FlowExchangeError:
		response = make_response(
			json.dumps('Failed to upgrade the authorization code.'), 401)
		response.headers['Content-Type'] = 'application/json'
		return response

	# Check that the access token is valid.
	access_token = credentials.access_token
	url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
		   % access_token)
	h = httplib2.Http()
	result = json.loads(h.request(url, 'GET')[1])
	# If there was an error in the access token info, abort.
	if result.get('error') is not None:
		response = make_response(json.dumps(result.get('error')), 500)
		response.headers['Content-Type'] = 'application/json'

	# Verify that the access token is used for the intended user.
	gplus_id = credentials.id_token['sub']
	if result['user_id'] != gplus_id:
		response = make_response(
			json.dumps("Token's user ID doesn't match given user ID."), 401)
		response.headers['Content-Type'] = 'application/json'
		return response

	# Verify that the access token is valid for this app.
	if result['issued_to'] != CLIENT_ID:
		response = make_response(
			json.dumps("Token's client ID does not match app's."), 401)
		print "Token's client ID does not match app's."
		response.headers['Content-Type'] = 'application/json'
		return response

	stored_credentials = login_session.get('credentials')
	stored_gplus_id = login_session.get('gplus_id')
	if stored_credentials is not None and gplus_id == stored_gplus_id:
		response = make_response(json.dumps('Current user is already connected.'),
								 200)
		response.headers['Content-Type'] = 'application/json'
		return response

	# Store the access token in the session for later use.
	login_session['credentials'] = credentials
	login_session['gplus_id'] = gplus_id

	# Get user info
	userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
	params = {'access_token': credentials.access_token, 'alt': 'json'}
	answer = requests.get(userinfo_url, params=params)

	data = answer.json()

	login_session['username'] = data["name"]
	login_session['picture'] = data["picture"]
	login_session['email'] = data["email"]

	# see if user exists, if it doesn't make a new one
	user_id = getUserID(data["email"])
	if user_id == 'None':
		user_id = createUser(login_session)
	login_session['user_id'] = user_id

	output = ''
	output += '<h1>Welcome, '
	output += login_session['username']
	output += '!</h1>'
	output += '<img src="'
	output += login_session['picture']
	output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
	flash("you are now logged in as %s" % login_session['username'])
	print "done!"
	# print login_session
	return output

# User Helper Functions


def createUser(login_session):
	newUser = User(name=login_session['username'], email_id=login_session[
				   'email'])
	session.add(newUser)
	session.commit()
	user = session.query(User).filter_by(email_id=login_session['email']).one()
	return user.id



def getUserInfo(user_id):
	user = session.query(User).filter_by(user_id=user_id).one()
	return user

def getUserID(email):
	try:
		user = session.query(User).filter_by(email_id=email).one()
		return user.user_id
	except:
		return None


# DISCONNECT - Revoke a current user's token and reset their login_session
@app.route('/gdisconnect')
def gdisconnect():
	 # Only disconnect a connected user.
	credentials = login_session.get('credentials')
	if credentials is None:
		response = make_response(
			json.dumps('Current user not connected.'), 401)
		response.headers['Content-Type'] = 'application/json'
		return response
	access_token = credentials.access_token
	url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
	print access_token
	h = httplib2.Http()
	result = h.request(url, 'GET')[0]
	# print 'result is '
	# print result
	if result['status'] == '200':
		del login_session['credentials']
		del login_session['gplus_id']
		del login_session['username']
		del login_session['email']
		del login_session['picture']

		response = make_response(json.dumps('Successfully disconnected.'), 200)
		response.headers['Content-Type'] = 'application/json'
		return redirect(url_for('allListings'))
	else:
		# For whatever reason, the given token was invalid.
		response = make_response(json.dumps('Failed to revoke token for given user.', 400))
		response.headers['Content-Type'] = 'application/json'
		return response


@app.route('/')
@app.route('/alllistings/')
def allListings():
	products = []
	heading = "All Listings"

	state = ''.join(random.choice(string.ascii_uppercase + string.digits) 
		for x in xrange(32))
	login_session['state'] = state

	products = (session.query(Listing.listing_id,Listing.product_id,Listing.deposit,Listing.max_days,Listing.is_available,
		Product.name,Product.description,Product.identifier,Product.identifier_value).join(Product)).filter(Listing.is_available == True).all()

	if 'username' not in login_session:
		return render_template('alllistingspublic.html',products = products, STATE=state)
	else:
		return render_template('alllistings.html',products = products, heading = heading, STATE=state)


@app.route('/mylistings')
def myListings():
	products = []
	heading = "My Listings"
	email = login_session['email']
	user_id = getUserID(email)
	state = ''.join(random.choice(string.ascii_uppercase + string.digits) 
		for x in xrange(32))
	login_session['state'] = state
	# listings = session.query(Listing).filter_by(user_id = user_id, is_available = True).all()
	# for listing in listings:
	# 	products.append(session.query(Product).filter_by(product_id = listing.product_id).one())

	products = (session.query(Listing.listing_id,Listing.product_id,Listing.deposit,Listing.max_days,Listing.is_available,
		Product.name,Product.description,Product.identifier,Product.identifier_value).join(Product)).filter(Listing.is_available == True).filter(Listing.user_id == user_id).all()

	if 'username' not in login_session:
		return render_template('alllistingspublic.html',products = products, STATE=state)
	else:
		return render_template('alllistings.html',products = products, heading = heading, STATE=state)


# Task 3: Create a route for deleteMenuItem function here

@app.route('/allusers/')
def allUsers():
	users = []	
	all_users = session.query(User).all()
	for user in all_users:
		users.append(session.query(User).filter_by(user_id = user.user_id).one())
	return render_template('allusers.html',users = users)

@app.route('/deleteuser/')
def delUser():
	mona_user = session.query(User).filter_by(user_id = 3).one()
	session.delete(mona_user)
	session.commit()

# Task 3: Create a route for deleteMenuItem function here

@app.route('/products/<int:product_id>/')
def productDetails(product_id):
	product = session.query(Product).filter_by(product_id = product_id).one()
	listing = session.query(Listing).filter_by(product_id = product_id).one()
	return render_template('productdetails.html',product = product, listing = listing)

# Task 3: Create a route for deleteMenuItem function here

@app.route('/products/new', methods=['GET', 'POST'])
def newListing():
	if 'username' not in login_session:
		return redirect('/login')
	user_id = login_session['user_id']
	if request.method == 'POST':
		newProduct = Product(name = request.form['name'], description = request.form['description'], category = request.form['category'], identifier = request.form['identifier'], identifier_value = request.form['identifier_value'])
		newProductListing = Listing(deposit = request.form['deposit'], max_days = request.form['max_days'], user_id = user_id, product = newProduct)
		session.add(newProduct)
		session.add(newProductListing)
		session.commit()
		return redirect(url_for('myListings'))
	else:
		return render_template('newlisting.html')

# Task 3: Create a route for deleteMenuItem function here

@app.route('/products/<int:product_id>/edit', methods=['GET', 'POST'])
def editListing(product_id):
	if 'username' not in login_session:
		return redirect('/login')
	editedProduct = session.query(Product).filter_by(product_id=product_id).one()
	editedList = session.query(Listing).filter_by(product_id=product_id).one()
	if login_session['user_id'] != editedList.user_id:
		return "<script>function myFunction() {alert('You are not authorized to edit this listing. Please create your own listing in order to edit listing details.');}</script><body onload='myFunction()''>"
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
		session.add(editedList)
		session.commit()
		return redirect(url_for('myListings'))
	else:
		return render_template('editlisting.html',product_id=product_id, product=editedProduct, listing=editedList)

# Task 3: Create a route for deleteMenuItem function here

@app.route('/products/<int:product_id>/delete', methods=['GET','POST'])
def deleteProduct(product_id):
	if 'username' not in login_session:
		return redirect('/login')
	deletedProduct = session.query(Product).filter_by(product_id=product_id).one()
	deletedList = session.query(Listing).filter_by(product_id=product_id).one()
	if login_session['user_id'] != deletedList.user_id:
		return "<script>function myFunction() {alert('You are not authorized to edit this listing. Please create your own listing in order to edit listing details.');}</script><body onload='myFunction()''>"
	if request.method == 'POST':
		if deletedProduct.product_id:
			deletedProduct.is_active = False
			deletedList.is_available = False
		session.add(deletedProduct)
		session.add(deletedList)
		session.commit()
		return redirect(url_for('myListings'))
	else:
		return render_template('deletelisting.html',product_id=product_id,product=deletedProduct, listing=deletedList)


if __name__ == '__main__':
	app.secret_key = 'super_secret_key'
	app.debug = True
	app.run(host='0.0.0.0', port=5000)