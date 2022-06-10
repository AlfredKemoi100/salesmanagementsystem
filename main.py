
#we import the flask class and the render templaate function to help us load HTML files in routes




from cProfile import label
from flask import Flask, redirect, render_template,request,redirect
import psycopg2

app = Flask(__name__)

#conn=psycopg2.connect(user="postgres",password="12345",
#host="127.0.0.1",port="5432",database="myduka")
conn=psycopg2.connect(user="svvdghcjnmuxaw",password="cd6fedb0da66fe4516cb59dcb8ce65cb4089ba9f6f15902b511ffe03e2abe93f",
host="ec2-3-248-121-12.eu-west-1.compute.amazonaws.com",port="5432",database="d5p7thrhgluvt8")
cur = conn.cursor()
cur.execute("CREATE TABLE IF NOT EXISTS products (id serial PRIMARY KEY,name VARCHAR(100),buying_price INT,selling_price INT,stock_quantity INT);")
cur.execute("CREATE TABLE IF NOT EXISTS sales (id serial PRIMARY KEY,pid INT, quantity INT, created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(), FOREIGN KEY(pid) REFERENCES products(id) ON DELETE CASCADE);")
conn.commit()

@app.route("/")
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
        pid=request.form['pid']
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

    # #inside the graph html change to the following
    # data: {
    #      labels:{{products_name| tojson}},
    #     datasets: [{
    #      label: 'profit per products',
    #      data:{{profit| tojson}}
                

       
    

app.run(port=22)


