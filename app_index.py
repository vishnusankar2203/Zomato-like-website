from flask import Flask, request, jsonify, render_template
import mysql.connector

app = Flask(__name__)


def create_connection():
    return mysql.connector.connect(
        host='localhost',
        user='root',
        password='root',
        database='zomato'
    )


# Home route
@app.route('/')
def home():
    return render_template('index.html')


# Place an order (POST)
@app.route('/place_order', methods=['POST'])
def place_order():
    connection = None
    cursor = None
    try:
        order_data = request.get_json()

        cart = order_data.get('cart')
        address = order_data.get('address')

        if not cart or not address:
            return jsonify({"error": "Cart is empty or address is missing."}), 400

        connection = create_connection()
        cursor = connection.cursor()

        user_id = 1  # Static user for demo purposes

        for item in cart:
            item_name = item.get('name')
            quantity = item.get('quantity')

            if not item_name or not quantity:
                continue  # Skip invalid items

            cursor.execute("SELECT item_id FROM items WHERE item_name = %s", (item_name,))
            result = cursor.fetchone()

            # Clear unread result if any
            while cursor.nextset():
                pass

            if not result:
                return jsonify({"error": f"Item '{item_name}' not found."}), 400

            item_id = result[0]

            insert_query = """
                INSERT INTO orders (user_id, item_id, quantity, delivery_address)
                VALUES (%s, %s, %s, %s)
            """
            cursor.execute(insert_query, (user_id, item_id, quantity, address))

        connection.commit()
        return jsonify({"message": "Order placed successfully!"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        if cursor:
            try:
                while cursor.nextset():
                    pass
            except:
                pass
            cursor.close()
        if connection:
            connection.close()


# Get all orders (GET)
@app.route('/orders', methods=['GET'])
def get_orders():
    connection = None
    cursor = None
    try:
        connection = create_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM orders")
        orders = cursor.fetchall()

        # Optional: You could format the output into a list of dicts
        return jsonify({"orders": orders}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


if __name__ == '__main__':
    app.run(debug=True)
