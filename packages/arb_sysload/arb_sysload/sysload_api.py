from flask import Flask, jsonify, request

from arb_sysload.utils import get_sysload_redis

app = Flask(__name__)
redis_client = get_sysload_redis()


@app.route('/checks', methods=['GET'])
def get_checks():
    # Retrieve all checks from Redis
    checks = {}
    for key in redis_client.keys():
        checks[key] = redis_client.hgetall(key)
    return jsonify(checks)


@app.route('/check/<check_name>/action', methods=['POST'])
def check_action(check_name):
    action = request.json.get("action")
    if action == "mute":
        # Implement muting logic here
        pass
    elif action == "disable":
        # Implement disabling logic here
        pass
    elif action == "relaunch":
        # Implement relaunching logic here
        pass
    else:
        return jsonify({"error": "Unknown action"}), 400
    return jsonify({"message":
                    f"Action {action} performed on {check_name}"}), 200


if __name__ == "__main__":
    app.run(debug=True)
