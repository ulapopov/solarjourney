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

@app.route('/')
def home():
    return render_template('index.html')  # Ensure you create this template in the templates folder

@socketio.on('message from user')
def handle_message(msg):
    try:
        '''       
        response = client.chat.completions.create(
          model="gpt-4-turbo-preview",
            messages=[
                {"role":"system","content": """Pretent you are a famous astrologist Angela Pearl. 
                You always generate positive predictions"""},
                {"role": "user", "content": msg}
            ],
          temperature=0.7,
          max_tokens=1024,
          top_p=1,
          frequency_penalty=0,
          presence_penalty=0,
        )
        '''
        #socketio.emit('message from server', response.choices[0].message.content)
        socketio.emit('message from server')
    except Exception as e:
        print(f"Error: {e}")
        socketio.emit('message from server', "Sorry, I couldn't process that message.")


if __name__ == '__main__':
    socketio.run(app, debug=True, allow_unsafe_werkzeug=True)


