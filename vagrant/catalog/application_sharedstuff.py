from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup_sharedstuff import User, Base, Product, Listing
from flask import session as login_session
import random, string

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

engine = create_engine('sqlite:///sharedstuff.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


@app.route('/login')
def showLogin():
	state = ''.join(random.choice(string.ascii_uppercase + string.digits) 
		for x in xrange(32))
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
	print access_token
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

	# stored_credentials = login_session.get('credentials')
	# stored_gplus_id = login_session.get('gplus_id')
	# if stored_credentials is not None and gplus_id == stored_gplus_id:

	stored_access_token = login_session.get('access_token')
	stored_gplus_id = login_session.get('gplus_id')
	if stored_access_token is not None and gplus_id == stored_gplus_id:
		response = make_response(json.dumps('Current user is already connected.'),
								 200)
		response.headers['Content-Type'] = 'application/json'
		return response

	# Store the access token in the session for later use.
	#login_session['credentials'] = credentials
	login_session['access_token'] = credentials.access_token
	login_session['gplus_id'] = gplus_id

	print "***************"
	print login_session['access_token']

	# Get user info
	userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
	params = {'access_token': credentials.access_token, 'alt': 'json'}
	answer = requests.get(userinfo_url, params=params)

	data = answer.json()

	login_session['username'] = data["name"]
	login_session['picture'] = data["picture"]
	login_session['email'] = data["email"]

	output = ''
	output += '<h1>Welcome, '
	output += login_session['username']
	output += '!</h1>'
	output += '<img src="'
	output += login_session['picture']
	output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
	flash("you are now logged in as %s" % login_session['username'])
	print "done!"
	return output

@app.route('/gdisconnect')
def gdisconnect():
	access_token = login_session['access_token']
	print access_token
	print 'In gdisconnect access token is %s', access_token
	print 'User name is: ' 
	print login_session['username']
	if access_token is None:
		print 'Access Token is None'
		response = make_response(json.dumps('Current user not connected.'), 401)
		response.headers['Content-Type'] = 'application/json'
		return response
	url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % login_session['access_token']
	h = httplib2.Http()
	result = h.request(url, 'GET')[0]
	print 'result is '
	print result
	if result['status'] == '200':
		del login_session['access_token'] 
		del login_session['gplus_id']
		del login_session['username']
		del login_session['email']
		del login_session['picture']
		response = make_response(json.dumps('Successfully disconnected.'), 200)
		response.headers['Content-Type'] = 'application/json'
		return response
	else:
	
		response = make_response(json.dumps('Failed to revoke token for given user.', 400))
		response.headers['Content-Type'] = 'application/json'
		return response


@app.route('/')
@app.route('/alllistings/')
def allListings():
	products = []

	state = ''.join(random.choice(string.ascii_uppercase + string.digits) 
		for x in xrange(32))
	login_session['state'] = state

	listings = session.query(Listing).filter_by(is_available = True).all()
	for listing in listings:
		products.append(session.query(Product).filter_by(product_id = listing.product_id).one())
	return render_template('alllistings.html',products = products, STATE=state)

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
	app.secret_key = 'super_secret_key'
	app.debug = True
	app.run(host='0.0.0.0', port=5000)