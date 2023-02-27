#we import the flask class and the render templaate function to help us load HTML files in routes

from cProfile import label

from flask import Flask, redirect, render_template,request, session, url_for
import psycopg2
import re
from datetime import timedelta
# from models import db, Users

app = Flask(__name__)
app.config["SECRET_KEY"] = "freddy100"
app.permanent_session_lifetime= timedelta(minutes=5)

conn=psycopg2.connect(user="postgres",password="12345", host="127.0.0.1",port="5432",database="myduka")
# conn=psycopg2.connect(user="rwutkwhzpqpasv",password="db2c720f6a8041c1689d37f6aa37793b0b28b5067f45d3aa3c274add0bd0d629",
# host="ec2-34-241-90-235.eu-west-1.compute.amazonaws.com",port="5432",database="d80lnmj6o22u6i")
cur = conn.cursor()
cur.execute("CREATE TABLE IF NOT EXISTS products (id serial PRIMARY KEY,name VARCHAR(100),buying_price INT,selling_price INT,stock_quantity INT);")
cur.execute("CREATE TABLE IF NOT EXISTS sales (id serial PRIMARY KEY,pid INT, quantity INT, created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(), FOREIGN KEY(pid) REFERENCES products(id) ON DELETE CASCADE);")
conn.commit()

cur.execute("CREATE TABLE IF NOT EXISTS users (id serial PRIMARY KEY,username VARCHAR(100),email VARCHAR(100),password VARCHAR(100));")
conn.commit()

@app.route("/register",methods = ['POST','GET'])
def register():
    if request.method =='POST':
        username = request.form['username']
        email = request.form['email'] 
        password = request.form['password']
        print('hi')
        cur.execute("""INSERT INTO users (username,email,password) VALUES(%(un)s,%(em)s,%(ps)s)""",{"un":username,"em":email,"ps":password})
        conn.commit()
        return redirect(url_for('login'))
    else:
        return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cur.execute("SELECT * FROM users WHERE username= %s and password= %s", (username,password))
        record= cur.fetchone()
        
        if record:
            pw= record[3]
            if pw== password:
                session.permanent= True   
                # session['loggedin']= True
                session['username']= record[1]
                session['id']= record[0]
                return redirect(url_for('home'))    
            else:
                return redirect(url_for('login'))
        else:
            return redirect(url_for('register'))
    return render_template('login.html')       

# @app.route('/logout')
# def logout():
#     session.pop('loggedin',None)
#     session.pop('username',None) 
#     return redirect(url_for('login'))   

@app.route("/")
def home1():
    #return a HTML file
    hello = "hello Freddy"
    return render_template("index.html",h=hello)

@app.route("/home")
def home():
    #return a HTML file
    hello = "hello Freddy"
    return render_template("index.html",h=hello)

#@app.route("/sales")
#def sales():
    cur.execute("SELECT * from sales")
    sales=cur.fetchall()
    print(sales)
    return render_template("sales.html",sales=sales)  


@app.route("/form_true",methods = ['POST','GET'])
def form():
    if request.method == 'GET':
        return render_template("form.html")
    else:
        first_name = request.form['fname']
        last_name = request.form['lname'] 
        print(first_name) 
        print(last_name) 
        return redirect("/form_true") 

@app.route("/products",methods = ['POST','GET'])
def form_data():
    if request.method == 'GET':
        cur.execute("SELECT * from products")
        products = cur.fetchall()
        
        return render_template("products.html",products=products)
    else:
        
        name = request.form['name']
        buying_price = request.form['bprice'] 
        selling_price = request.form['sprice']
        stock_quantity = request.form['qt']
         
        print(name) 
        print(buying_price)
        print(selling_price)
        print(stock_quantity) 
        cur.execute("""INSERT INTO products (name,buying_price,selling_price,stock_quantity) VALUES(%(n)s,%(bp)s,%(sp)s,%(st)s)""",{"n":name,"bp":buying_price,"sp":selling_price,"st":stock_quantity})
        conn.commit()
        return redirect("/products") 

@app.route("/sales",methods=['POST','GET'])
def sales():
    if request.method=='POST':
        quantity=request.form['quantity']
        quantity=(int(quantity))
        pid=request.form['pid']
        cur.execute( """select stock_quantity from products where id=%(pid)s""",{"pid":pid})
        current_quantity=cur.fetchone()
        print(current_quantity)
        print(type(current_quantity))
        print(type(current_quantity[0]))
        current_quantity=current_quantity[0]
        stock_quantity=current_quantity-quantity
        print(stock_quantity)
        cur.execute("""update products set stock_quantity=%(stock_quantity)s where id=%(pid)s""", {"pid":pid, "stock_quantity": stock_quantity})
        # print(type(current_quantity))
        
        cur.execute("INSERT INTO sales (pid,quantity) VALUES(%s,%s)",(pid,quantity))
        conn.commit()
        return redirect("/products")
    else:
        cur.execute("SELECT * from sales")
        sales=cur.fetchall()
        print(sales)
        return render_template("sales.html",sales=sales)
        

@app.route("/sales/<int:id>")
def sale(id):
    x=id
    cur.execute("""SELECT * FROM sales WHERE pid=%(id)s""",{"id":x})
    sales=cur.fetchall()
    return render_template("sales.html",sales=sales)  

#alterenative insert query
# cur.execute("INSERT INTO products (id,name,buying_price,selling_price,stock_quantity)
# VALUES (%s,%s,%s,%s,%s,)",(id,name,buying_price,selling_price,stock_quantity))               
   
@app.route("/dashboard")
def dashboard():
    cur.execute("""select sum((products.selling_price-products.buying_price)*sales.quantity)as profit, products.name from sales
    join products on products.id=sales.pid
    GROUP BY products.name""")
    graph=cur.fetchall()
    print(graph)
    product_name=[]
    profit=[]
    for tpl in graph:
        product_name.append(tpl[1])
        print(product_name)
        for tpl in graph:
            profit.append(tpl[0])
    print(profit)  
    print(product_name)      
    return render_template("dashboard.html",product_name=product_name,profit=profit)

@app.route('/delete/<int:id>')
def product_delete(id):
    id=id
    cur.execute("""delete from products where id=%(id)s""",{"id":id})
    conn.commit()
    return redirect('/products')

    # #inside the graph html change to the following
    # data: {
    #      labels:{{products_name| tojson}},
    #     datasets: [{
    #      label: 'profit per products',
    #      data:{{profit| tojson}}
    
@app.route("/edit_product/<int:x>", methods=["POST", "GET"])
def edit_product(x):
   
    if request.method == "POST":
        name = request.form['name']
        buying_price = request.form['bprice'] 
        selling_price = request.form['sprice']
        stock_quantity = request.form['qt']
        print (request.form)
        cur.execute(
            "UPDATE products SET name = %(name)s, buying_price = %(bprice)s, selling_price = %(sprice)s, stock_quantity = %(qt)s WHERE id=%(x)s",
            {"x":x,"name":name,"bprice":buying_price,"sprice":selling_price,"qt":stock_quantity}
        )
        conn.commit()
        return redirect(url_for("dashboard"))
    else:   
        return render_template("home")

# @app.route("/print")
# def task():
#     hi = "hello world"
#     print(hi) 
#     return render_template("index.html",h=hi)       



if __name__== "__main__":
    app.run(port=5080)


