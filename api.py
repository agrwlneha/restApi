import flask 
import sqlite3
from flask import Flask, render_template, request, json, jsonify

app = Flask(__name__)
app.config["DEBUG"] = True

USER_DB = "users.db"

def createDatabase():
	db = sqlite3.connect(USER_DB)
	print "database opened successfully"
	db.execute('CREATE TABLE users (id NUMBER, first_name TEXT, last_name TEXT, company_name TEXT, city TEXT, state TEXT, zip NUMBER, email TEXT, web TEXT, age NUMBER)')
	print "table created"
	db.close()

@app.route('/api/users', methods = ['GET'])
def getAll():
	try:
		connection = sqlite3.connect(USER_DB)
		connection.row_factory = sqlite3.Row
		cursor = connection.cursor()
		if 'id' in request.args:
	 		id = request.args['id']
	 		cursor.execute("SELECT * FROM users WHERE id= (?)", (id,))
	 		listOfUsers = cursor.fetchall()
			items = []
			for row in listOfUsers:
				items.append({'id': row['id'], 'first_name': row['first_name'], 'last_name': row['last_name'], 'company_name': row['company_name'], 'state': row['state'], 'city': row['city'], 'zip': row['zip'], 'email': row['email'], 'web': row['web'], 'age': row['age']})
			return jsonify({'users': items})
		else:
			sql = "SELECT * FROM users"
			if 'name' in request.args:
				name = request.args['name']
				sql = sql + " WHERE first_name LIKE '%" + name+ "%' " + " OR last_name LIKE '%" + name+"%' "
			if 'sort' in request.args:
				input_sort = request.args['sort']
				if input_sort[0] == '-':
					input_sort = input_sort[1:]
					sql = sql + " ORDER BY " + input_sort + " DESC "
				else:
					sql = sql + " ORDER BY " + input_sort + " ASC "
			if 'limit' in request.args:
				input_limit = request.args['limit']
				if 'page' in request.args:
					input_page = request.args['page']	
					offset = int(input_page) * int(input_limit)
					if offset > 0:
						sql = sql + " LIMIT " + input_limit + " , " + str(offset)
					else:
						sql = sql + " LIMIT " + input_limit
				else:
					sql = sql + " LIMIT " + input_limit
			else:
				sql = sql + " LIMIT 5 "
			cursor.execute(sql)
		listOfUsers = cursor.fetchall()
		items = []
		for row in listOfUsers:
			items.append({'id': row['id'], 'first_name': row['first_name'], 'last_name': row['last_name'], 'company_name': row['company_name'], 'state': row['state'], 'city': row['city'], 'zip': row['zip'], 'email': row['email'], 'web': row['web'], 'age': row['age']})
		return jsonify({'users': items})
	except:
		connection.rollback()
		msg = "Error in GET"
		return render_template('result.html', value=msg)
	finally:
		connection.close()

@app.route('/api/users',  methods = ['POST'])
def addRecord():
	if request.headers['Content-Type'] == 'application/json':
		id = json.dumps(request.json['id'])
		first_name = json.dumps(request.json['first_name']).strip('\"')
		last_name = json.dumps(request.json['last_name']).strip('\"')
		company_name = json.dumps(request.json['company_name']).strip('\"')
		state = json.dumps(request.json['state']).strip('\"')
		city = json.dumps(request.json['city']).strip('\"')
		zip = json.dumps(request.json['zip'])
		email = json.dumps(request.json['email']).strip('\"')
		web = json.dumps(request.json['web']).strip('\"')
		age = json.dumps(request.json['age'])
		try:
			connection =  sqlite3.connect(USER_DB)
			cursor = connection.cursor()
			cursor.execute("INSERT INTO users (id,first_name,last_name,company_name,city,state,zip,email,web,age) VALUES (?,?,?,?,?,?,?,?,?,?)", (id,first_name,last_name,company_name,city,state,zip,email,web,age))
			connection.commit()
			msg = "Added user successfully"
			# send html code 201 on success
			return render_template('result.html', value = msg), 201
		except:
			connection.rollback()
			msg = "Error in POST"
			return render_template('result.html', value = msg)
		finally:
			connection.close()
	else:
		return "Unsupported Media Type"		

@app.route('/api/users', methods=['DELETE'])
def deleteRecord():
	if 'id' in request.args:
	 	id = request.args['id']
		try:
			connection = sqlite3.connect(USER_DB)
			cursor = connection.cursor()
			cursor.execute("SELECT * FROM users WHERE 	id=(?)", id)
			cursor.execute("DELETE FROM users WHERE id=(?)",(id,))
			connection.commit()
			msg = "Deleted user successfully"
			return render_template('result.html', value=msg), 200
		except:
			connection.rollback()
			msg = "Error in DELETE"
			return render_template('result.html', value=msg)
		finally:
			connection.close()
	else:
		return "Invalid request. Id not found"

@app.route('/api/users' , methods=['PUT'])
def updateRecord():
	if 'id' in request.args:
	 	id = request.args['id']
		try:
			connection = sqlite3.connect(USER_DB)
			sql = "SET "
			data = json.loads(json.dumps(request.json))
			if 'first_name' in data:
				first_name = json.dumps(request.json['first_name']).strip('\"')
				sql = sql + "first_name = '" + first_name + "' , "
			if 'last_name' in data:
				last_name = json.dumps(request.json['last_name']).strip('\"')
				sql = sql + "last_name = '" + last_name + "' , "
			if 'company_name' in data:
				company_name = json.dumps(request.json['company_name']).strip('\"')
				sql = sql + "company_name = '" + company_name + "' , "
			if 'state' in data:
				state = json.dumps(request.json['state']).strip('\"')
				sql = sql + "state = '" + state + "' , "
			if 'city' in data:
				city = json.dumps(request.json['city']).strip('\"')
				sql = sql + "city = '" + city + "' , "
			if 'zip' in data:
				zip = json.dumps(request.json['zip'])
				sql = sql + "zip = " + zip + " , "
			if 'email' in data:
				email = json.dumps(request.json['email']).strip('\"')
				sql = sql + "email = '"  + email + "' , "
			if 'web' in data:
				web = json.dumps(request.json['web']).strip('\"')
				sql = sql + "web = '" + web + "' , "
			if 'age' in data:
				age = json.dumps(request.json['age'])
				sql = sql + "age = " + age + " , "
			#remove last ', ' from sql
			sql = sql[:-2]
			sql = "UPDATE users " + sql + "WHERE id = " + id
			cursor = connection.cursor()			
			cursor.execute(sql)
			connection.commit()
			msg = "User updated"
			return render_template('result.html', value = msg), 200
		except:
			connection.rollback()
			msg = "ERROR in PUT"
			return render_template('result.html', value = msg)
		finally:
			connection.close()
	else:
		return "Invalid request. Id not found"

app.run()