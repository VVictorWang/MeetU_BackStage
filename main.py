import json

from flask_init import app

import user
import needs

@app.errorhandler(500)
def internal_server_error(e):
    return json.dumps({'error': 'Unexpected error!'}), 500, {'content-type': 'application/json'}


@app.errorhandler(405)
def methods_not_allowed(e):
    return json.dumps({'error': 'method not allowed'}), 405, {'content-type': 'application/json'}


@app.errorhandler(404)
def source_not_found(e):
    return json.dumps({'error': '404 Not Found'}), 404, {'content-type': 'application/json'}


if __name__ == '__main__':
    app.run(host='0.0.0.0', port='8889')
