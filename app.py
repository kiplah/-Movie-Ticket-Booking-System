# app.py
from flask import Flask, render_template, request, redirect, url_for, jsonify, send_file
from datetime import datetime
import json
import os
import matplotlib.pyplot as plt
import io

app = Flask(__name__)

DATA_FILE = 'data/sales_data.json'

# Helper functions to load and save data
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as file:
            return json.load(file)
    return {}

def save_data(data):
    with open(DATA_FILE, 'w') as file:
        json.dump(data, file)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/book', methods=['POST'])
def book_ticket():
    movie_data = load_data()
    movie_title = request.form['movie_title']
    showtime = request.form['showtime']
    customer_name = request.form['customer_name']
    tickets = int(request.form['tickets'])

    if movie_title not in movie_data:
        movie_data[movie_title] = {"showtime": showtime, "total_seats": 100, "tickets_sold": 0, "sales_data": []}

    if movie_data[movie_title]["tickets_sold"] + tickets <= movie_data[movie_title]["total_seats"]:
        movie_data[movie_title]["tickets_sold"] += tickets
        movie_data[movie_title]["sales_data"].append({"time": datetime.now().isoformat(), "tickets": tickets})
        save_data(movie_data)
        return redirect(url_for('view_sales'))
    else:
        return "Not enough seats available.", 400

@app.route('/sales')
def view_sales():
    movie_data = load_data()
    return render_template('sales.html', movie_data=movie_data)

@app.route('/sales_chart.png')
def sales_chart():
    movie_data = load_data()
    
    # Prepare data for plotting
    movies = list(movie_data.keys())
    tickets_sold = [movie_data[movie]["tickets_sold"] for movie in movies]

    # Create bar chart
    plt.figure(figsize=(10, 6))
    plt.bar(movies, tickets_sold, color='skyblue')
    plt.xlabel('Movie Titles')
    plt.ylabel('Tickets Sold')
    plt.title('Tickets Sold Per Movie')
    plt.xticks(rotation=45, ha='right')
    
    # Save the plot to a BytesIO object and return it as a response
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plt.close()
    return send_file(img, mimetype='image/png')

if __name__ == '__main__':
    app.run(debug=True)
