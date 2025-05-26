from flask import Flask, jsonify, render_template, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

@app.route('/', methods=["GET", "POST"])
@app.route('/')
def index():
    return render_template('index.html')






@app.route('/api/data')
async def get_data():
    if  request.method == "POST":
        print ("in the post")
        username = request.form.get("username")
        print (username)
    if  request.method == "GET":
        print ("in the get")
        username = request.form.get("username")
        print (username)
    # Perform asynchronous operations here
    data = {'message': 'Hello from Flask!'}
    return data


def index2():
    username=""
    if  request.method == "POST":
        print ("in the post")
        username = request.form.get("username")
        print (username)
        return jsonify(username)
        #return render_template("index.html", result=username)
    if  request.method == "GET":
        print ("in the get")
        
        print (username)
        return render_template("index.html", result=username)
   
    return render_template("index.html")

if __name__ == '__main__':
    app.run(debug=True)




