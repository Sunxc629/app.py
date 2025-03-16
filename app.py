from flask import Flask, request, jsonify
from flask_restful import Api, Resource
import base64

app = Flask(__name__)
api = Api(app)

users = {}

class SignUp(Resource):
    def post(self):
        data = request.get_json()
        user_id = data.get("user_id")
        password = data.get("password")
        nickname = data.get("nickname", user_id)
        comment = data.get("comment", "")

        if not user_id or not password:
            return {"message": "Account creation failed", "cause": "Required user_id and password"}, 400
        if user_id in users:
            return {"message": "Account creation failed", "cause": "User ID already exists"}, 400

        users[user_id] = {"password": password, "nickname": nickname, "comment": comment}
        return {"message": "Account success", "user": {"user_id": user_id, "nickname": nickname}}, 200

api.add_resource(SignUp, "/signup")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
