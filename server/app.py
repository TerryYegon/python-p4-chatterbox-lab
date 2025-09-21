#!/usr/bin/env python3

from flask import Flask, request, make_response, jsonify
from flask_migrate import Migrate
from flask_cors import CORS

from models import db, Message

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

CORS(app)  # enable cross-origin for frontend
migrate = Migrate(app, db)
db.init_app(app)

@app.route('/')
def home():
    return '<h1>Messages API</h1>'


# -------- GET ALL MESSAGES -------- #
@app.route('/messages', methods=['GET'])
def get_messages():
    messages = Message.query.order_by(Message.created_at.asc()).all()
    return make_response(jsonify([m.to_dict() for m in messages]), 200)


# -------- CREATE MESSAGE -------- #
@app.route('/messages', methods=['POST'])
def create_message():
    data = request.get_json()   # <-- FIX: use JSON, not form

    new_message = Message(
        body=data.get("body"),
        username=data.get("username")
    )

    db.session.add(new_message)
    db.session.commit()

    return make_response(jsonify(new_message.to_dict()), 201)

# -------- UPDATE MESSAGE -------- #
@app.route('/messages/<int:id>', methods=['PATCH'])
def update_message(id):
    data = request.get_json()
    message = db.session.get(Message, id)  # modern way instead of Query.get()

    if not message:
        return make_response({"error": "Message not found"}, 404)

    if "body" in data:
        message.body = data["body"]
        db.session.commit()

    return make_response(jsonify(message.to_dict()), 200)


# -------- DELETE MESSAGE -------- #
@app.route('/messages/<int:id>', methods=['DELETE'])
def delete_message(id):
    message = Message.query.get(id)

    if not message:
        return make_response(jsonify({"error": "Message not found"}), 404)

    db.session.delete(message)
    db.session.commit()

    return make_response(jsonify({"message": "Message deleted"}), 200)


if __name__ == '__main__':
    app.run(port=5555, debug=True)
