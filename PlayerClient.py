import os
import json
from dotenv import load_dotenv

import paho.mqtt.client as paho
from paho import mqtt
import time
import random

#Code given by TA's
def on_connect(client, userdata, flags, rc, properties=None):
    print("CONNACK received with code %s." % rc)

def on_publish(client, userdata, mid, properties=None):
    print("mid: " + str(mid))

def on_subscribe(client, userdata, mid, granted_qos, properties=None):
    print("Subscribed: " + str(mid) + " " + str(granted_qos))

def on_message(client, userdata, msg):
    #print(f"Message received on {msg.topic}: {msg.payload.decode()}")
    if msg.topic.endswith('/game_state'):
        try:
            data = json.loads(msg.payload.decode()) #load data 
            curr_pos = data.get("currentPosition", [])
            coins = data.get("coin1", []) + data.get("coin2", []) + data.get("coin3", [])
            walls = data.get("walls", [])

            # move is random, but away from walls
            move = random_valid_move(curr_pos, walls)
            if move:
                client.publish(f"games/{userdata['lobby_name']}/{userdata['player_name']}/move", move, qos=1)
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
        except KeyError as e:
            print(f"Key error in JSON data: {e}")

def random_valid_move(position, walls): #make a random move that strays from walls
    moves = ['UP', 'DOWN', 'LEFT', 'RIGHT']
    valid_moves = []
    for move in moves:
        next_pos = simulate_move(position, move)
        if next_pos not in walls:
            valid_moves.append(move) #make sure next move is not in walls
    return random.choice(valid_moves) if valid_moves else None

def simulate_move(position, move):
    x, y = position
    if move == 'UP':
        return [x - 1, y]
    elif move == 'DOWN':
        return [x + 1, y]
    elif move == 'LEFT':
        return [x, y - 1]
    elif move == 'RIGHT':
        return [x, y + 1]
    return position

if __name__ == '__main__':
    load_dotenv(dotenv_path='./credentials.env')
    
    broker_address = os.environ.get('BROKER_ADDRESS')
    broker_port = int(os.environ.get('BROKER_PORT'))
    username = os.environ.get('USER_NAME')
    password = os.environ.get('PASSWORD')
    
    players = ['Eugene', 'Ned', 'Ben', 'Matt']
    clients = []
    team_names = ['Ballers', 'Losers']
    lobby_name = "GAME"

    for i, player_name in enumerate(players):
        userdata = {'player_name': player_name, 'lobby_name': lobby_name}
        client = paho.Client(callback_api_version=paho.CallbackAPIVersion.VERSION1,client_id=player_name, userdata=userdata, protocol=paho.MQTTv5)
        
        client.tls_set(tls_version=mqtt.client.ssl.PROTOCOL_TLS)
        client.username_pw_set(username, password)
        client.connect(broker_address, broker_port)

        client.on_subscribe = on_subscribe
        client.on_message = on_message
        client.on_publish = on_publish
        client.loop_start()

        client.subscribe(f"games/{lobby_name}/{player_name}/game_state", qos=1)

        client.publish("new_game", json.dumps({
            'lobby_name': lobby_name,
            'team_name': team_names[i % 2],
            'player_name': player_name
        }), qos=1)
        clients.append(client)

    time.sleep(1)  # wait and then start the game
    clients[0].publish(f"games/{lobby_name}/start", "START", qos=1)

    try:
        # Keep the clients running, one for each player
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Game interrupted by user")
    finally:
        for client in clients:
            client.loop_stop()
            client.disconnect()
