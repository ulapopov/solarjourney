import logging
import openai
import os
import sys

from datetime import datetime
from flask import Flask, render_template, request
from flask_socketio import SocketIO
from logging import StreamHandler
from openai import OpenAI

openai.api_key = os.getenv('OPENAI_API_KEY')
client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
)

app = Flask(__name__)

# Setup basic configuration
#logging.basicConfig(level=logging.INFO)

stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setLevel(logging.INFO)
app.logger.addHandler(stream_handler)
app.logger.setLevel(logging.INFO)

# @app.before_request
# def before_request_logging():
# data = request.data or request.form or None
# logging.info(f"{datetime.now()} - Request: {request.method} {request.url} - Data: {data}")
#
# @app.after_request
# def after_request_logging(response):
# # Log basic response details without attempting to access the body directly
# logging.info(f"{datetime.now()} - Request: {request.method} {request.path} - Response: {response.status}")
# return response

memory = []

@app.route('/')
def home():
    app.logger.info('Home page requested')
    return render_template('index.html')

app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

@socketio.on('message from user')
def handle_message(msg):
    try:
        app.logger.info(f"{datetime.now()} - User Input: {msg}")
        memory.append({"role": "user", "content": msg})  # Add the new user message to memory

        # Limit the memory to the last 5 messages, adjust the number as needed
        if len(memory) > 5:
            memory.pop(0)  # Remove the oldest message if memory exceeds the limit

        # The actual call to the OpenAI API
        response = client.chat.completions.create(
            model="gpt-3.5-turbo-0125",
            messages=[
                {"role": "system", "content": """Pretend you are a famous astrologist Seraphima Bliss. 
                            You always generate positive predictions. Be short. Never add any hashtags."""},
                *memory
            ],
            temperature=0.2,
            max_tokens=4096,
            frequency_penalty=0.5,
            presence_penalty=0,
        )

        # Extracting the content from the response
        response_content = response.choices[0].message.content
        app.logger.info(f"{datetime.now()} - Model Response: {response_content}")

        # Emit the response back to the client
        socketio.emit('message from server', response_content)
        memory.append({"role": "assistant", "content": response_content})  # Add AI response to memory

    except Exception as e:
        error_message = f"Error calling OpenAI API: {e}"
        app.logger.error(f"{datetime.now()} - {error_message}")
        socketio.emit('message from server', f"Sorry, I couldn't process that message. Error: {e}")


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5001))
    socketio.run(app, debug=True, port=port, allow_unsafe_werkzeug=True)



