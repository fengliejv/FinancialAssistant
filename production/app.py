from flask import Flask, request

from production.wrapper.openai import get_agent_executor
from model.result import Result

from flask_cors import CORS, cross_origin
app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
@app.route('/hello', methods=['POST'])
@cross_origin()
def hello_world():
   return {
      "result": 'Hello World'
   }

@app.route("/message", methods=['POST'])
def message():
   if request.method == 'POST':
      data = request.get_json()
      session_id = str(data.get('sessionId'))
      message_info = str(data.get('messageInfo'))
      executor = get_agent_executor(session_id)
      result = executor.invoke(
          {"input": message_info},
          config={"configurable": {"session_id": session_id}},
      )
      return Result(200,result['output']).to_json()
   else:
      return Result(400,'This route only handles POST requests.').to_json()


if __name__ == '__main__':
   app.run()