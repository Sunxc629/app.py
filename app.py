from flask import Flask, request, jsonify
from flask_restful import Api, Resource
import base64
import re

app = Flask(__name__)
api = Api(app)

users = {}

def authenticate():
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Basic "):
        return None
    try:
        auth_decoded = base64.b64decode(auth_header.split(" ")[1]).decode("utf-8")
        user_id, password = auth_decoded.split(":", 1)
        if user_id in users and users[user_id]["password"] == password:
            return user_id
    except:
        pass
    return None

class SignUp(Resource):
    def post(self):
        data = request.get_json()
        user_id = data.get("user_id")
        password = data.get("password")
        nickname = data.get("nickname", user_id)
        comment = data.get("comment", "")

        if not user_id or not password:
            return {"message": "Account creation failed", "cause": "Required user_id and password"}, 400
        if not (6 <= len(user_id) <= 20 and re.match(r"^[A-Za-z0-9]+$", user_id)):
            return {"message": "Account creation failed", "cause": "Invalid user_id"}, 400
        if not (8 <= len(password) <= 20 and re.match(r"^[A-Za-z0-9!@#$%^&*()_+=-]+$", password)):
            return {"message": "Account creation failed", "cause": "Invalid password"}, 400
        if user_id in users:
            return {"message": "Account creation failed", "cause": "User ID already exists"}, 400

        users[user_id] = {"password": password, "nickname": nickname, "comment": comment}
        return {"message": "Account successfully created", "user": {"user_id": user_id, "nickname": nickname}}, 200


class GetUser(Resource):
    def get(self, user_id):
        auth_user = authenticate()
        if not auth_user:
            return {"message": "Authentication failed"}, 401
        if user_id not in users:
            return {"message": "No user found"}, 404

        user_info = users[user_id].copy()
        del user_info["password"]
        return jsonify({"message": "User details", "user": user_info}), 200


class UpdateUser(Resource):
    def patch(self, user_id):
        auth_user = authenticate()
        if not auth_user or auth_user != user_id:
            return {"message": "Authentication failed"}, 401
        if user_id not in users:
            return {"message": "No user found"}, 404

        data = request.get_json()
        if "user_id" in data or "password" in data:
            return {"message": "User update failed", "cause": "Not updateble user_id and password"}, 400

        if "nickname" in data:
            if not (1 <= len(data["nickname"]) <= 30):  
                return {"message": "User update failed", "cause": "Invalid nickname or comment"}, 400
            users[user_id]["nickname"] = data["nickname"]
        if "comment" in data:
            if not (0 <= len(data["comment"]) <= 100):  
                return {"message": "User update failed", "cause": "Invalid comment"}, 400
            users[user_id]["comment"] = data["comment"]

        return {"message": "User updated", "user": users[user_id]}, 200


class DeleteUser(Resource):
    def post(self):
        auth_user = authenticate()
        if not auth_user:
            return {"message": "Authentication failed"}, 401
        if auth_user not in users:
            return {"message": "User not found"}, 404

        del users[auth_user]
        return {"message": "Account and user successfully removed"}, 200


api.add_resource(SignUp, "/signup")
api.add_resource(GetUser, "/users/<string:user_id>")
api.add_resource(UpdateUser, "/users/<string:user_id>")
api.add_resource(DeleteUser, "/close")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
