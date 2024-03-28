import redis
import json

redis_client = redis.Redis(host="127.0.0.1", port=6379, db=0, password="p@ss$12E4")

msg = {
    "signal":1
}

redis_client.publish("MSFT_trade", json.dumps(msg))