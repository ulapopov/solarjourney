import openai
import os

from flask import Flask, render_template
from flask_socketio import SocketIO
from openai import OpenAI

os.environ["OPENAI_API_KEY"] = "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"
openai.api_key = os.getenv('OPENAI_API_KEY')
client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

memory = []

@app.route('/')
def home():
    return render_template('index.html')  # Ensure you create this template in the templates folder

@socketio.on('message from user')
def handle_message(msg):
    try:
        memory.append({"role": "user", "content": msg})  # Add the new user message to memory
  # Add the new message to memory

        if len(memory) > 5:
            memory.pop(0)  # Remove the oldest message if memory exceeds 3 messages

        response = client.chat.completions.create(
            model="gpt-3.5-turbo-0125",
            messages=[
                {"role": "system", "content": """Pretent you are a famous astrologist Angela Pearl. 
                You always generate positive predictions. Be short."""},
                *memory
            ],
            temperature=0.2,
            max_tokens=4096,
            #top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
        )

        memory.append({"role": "assistant", "content": response.choices[0].message.content})  # Add AI response to memory
        socketio.emit('message from server', response.choices[0].message.content)
    except Exception as e:
        print(f"Error: {e}")
        socketio.emit('message from server', f"Sorry, I couldn't process that message. Error: {e}")


if __name__ == '__main__':
    socketio.run(app, debug=True, port=5001, allow_unsafe_werkzeug=True)


