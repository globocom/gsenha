#!/usr/bin/env python
from gsenhaapi import app

if __name__ == '__main__':
	port = 8080
	print 'Starting server on port:{0}'.format(port)
	app.run(host='127.0.0.1', port=port, debug=True)