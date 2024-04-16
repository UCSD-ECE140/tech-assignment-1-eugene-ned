import os
import json
from dotenv import load_dotenv

import paho.mqtt.client as paho
from paho import mqtt
import time


# setting callbacks for different events to see if it works, print the message etc.
def on_connect(client, userdata, flags, rc, properties=None):
    """
        Prints the result of the connection with a reasoncode to stdout ( used as callback for connect )
        :param client: the client itself
        :param userdata: userdata is set when initiating the client, here it is userdata=None
        :param flags: these are response flags sent by the broker
        :param rc: stands for reasonCode, which is a code for the connection result
        :param properties: can be used in MQTTv5, but is optional
    """
    print("CONNACK received with code %s." % rc)


# with this callback you can see if your publish was successful
def on_publish(client, userdata, mid, properties=None):
    """
        Prints mid to stdout to reassure a successful publish ( used as callback for publish )
        :param client: the client itself
        :param userdata: userdata is set when initiating the client, here it is userdata=None
        :param mid: variable returned from the corresponding publish() call, to allow outgoing messages to be tracked
        :param properties: can be used in MQTTv5, but is optional
    """
    print("mid: " + str(mid))


# print which topic was subscribed to
def on_subscribe(client, userdata, mid, granted_qos, properties=None):
    """
        Prints a reassurance for successfully subscribing
        :param client: the client itself
        :param userdata: userdata is set when initiating the client, here it is userdata=None
        :param mid: variable returned from the corresponding publish() call, to allow outgoing messages to be tracked
        :param granted_qos: this is the qos that you declare when subscribing, use the same one for publishing
        :param properties: can be used in MQTTv5, but is optional
    """
    print("Subscribed: " + str(mid) + " " + str(granted_qos))


# print message, useful for checking if it was successful

def on_message(client, userdata, msg):
    """
        Prints a mqtt message to stdout ( used as callback for subscribe )
        :param client: the client itself
        :param userdata: userdata is set when initiating the client, here it is userdata=None
        :param msg: the message with topic and payload
    """

    print(f"Message received on {msg.topic}: {msg.payload}")

    

def move_towards_coin(game_state, player_name):
    # Extract player position and coin positions from game state
    player_pos = game_state['players'][player_name]['position']
    coins = game_state['coins']
    if not coins:
        return 'STOP'  # No more coins

    # Find the nearest coin
    nearest_coin = min(coins, key=lambda c: abs(c[0] - player_pos[0]) + abs(c[1] - player_pos[1]))
    # Decide move based on relative position of the nearest coin
    if nearest_coin[0] > player_pos[0]:
        return 'DOWN'
    elif nearest_coin[0] < player_pos[0]:
        return 'UP'
    elif nearest_coin[1] > player_pos[1]:
        return 'RIGHT'
    elif nearest_coin[1] < player_pos[1]:
        return 'LEFT'


if __name__ == '__main__':
    load_dotenv(dotenv_path='./credentials.env')
    
    broker_address = os.environ.get('BROKER_ADDRESS')
    broker_port = int(os.environ.get('BROKER_PORT'))
    username = os.environ.get('USER_NAME')
    password = os.environ.get('PASSWORD')
    
    players = ['Player1', 'Player2', 'Player3', 'Player4']
    clients = []
    team_name = ['TeamA', 'TeamB']
    lobby_name = "game_lobby"

    for i, player_name in enumerate(players):
        userdata = {
        'player_name': player_name,
        'lobby_name': lobby_name
    }
        client = paho.Client(callback_api_version=paho.CallbackAPIVersion.VERSION1, client_id=player_name, userdata=None, protocol=paho.MQTTv5)
        print(player_name)
        # enable TLS for secure connection
        client.tls_set(tls_version=mqtt.client.ssl.PROTOCOL_TLS)
        # set username and password
        client.username_pw_set(username, password)
        # connect to HiveMQ Cloud on port 8883 (default for MQTT)
        client.connect(broker_address, broker_port)

        # setting callbacks, use separate functions like above for better visibility

        client.on_subscribe = on_subscribe # Can comment out to not print when subscribing to new topics
        client.on_message = on_message
        client.on_publish = on_publish # Can comment out to not print when publishing to topics
        client.loop_start()

        # Dynamic game configuration
        '''
        lobby_name =  input("Enter lobby name: ")
        player_name = input("Enter your player name: ")
        team_name = input("Enter your team name: ")
        '''
        time.sleep(1)
        client.subscribe(f"games/{lobby_name}/lobby",qos=1)
        client.subscribe(f"games/{lobby_name}/{player_name}/game_state",qos=1)
        client.subscribe(f'games/{lobby_name}/scores',qos=1)
        
        # Register the player and subscribe to relevant topics

        client.publish("new_game", json.dumps({
            'lobby_name': lobby_name,
            'team_name': team_name[i % 2],
            'player_name': player_name
        }),qos=1)
        clients.append(client)
        '''
        time.sleep(1)
        client.publish(f"games/{lobby_name}/start", "START")
        # Game Loop for movement commands
        while True:
            move = input("Enter your move (UP, DOWN, LEFT, RIGHT, STOP to end): ")
            if move == "STOP":
                client.publish(f"games/{lobby_name}/start", "STOP", qos=1)
                break
            client.publish(f"games/{lobby_name}/{player_name}/move", move, qos=1)
            '''
    client.publish(f"games/{lobby_name}/start", "START")
    

    for client in clients:
            client.loop_stop()
            client.disconnect()
    
 