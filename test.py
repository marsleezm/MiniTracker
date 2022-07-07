from flask import Flask
from flask_restx import Resource, Api

app = Flask(__name__)
api = Api(app)

class Haha:
    @api.route('/hello')
    def get(self):
        return {'hello': 'world'}

if __name__ == '__main__':
    app.run(debug=True)
