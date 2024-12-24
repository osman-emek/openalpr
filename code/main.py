import json
import base64
import os

import tornado.ioloop
import tornado.web

import subprocess  

class MainHandler(tornado.web.RequestHandler):
    def post(self):
        try:
            payload = json.loads(self.request.body)
        except json.JSONDecodeError:
            self.set_status(400)
            self.finish('Invalid JSON payload')
            return

        if 'base64' not in payload:
            self.set_status(400)
            self.finish('"base64" parameter not provided')
            return

        base64_string = payload.get('base64')
        try:
            jpeg_bytes = base64.b64decode(base64_string)
        except base64.binascii.Error:
            self.set_status(400)
            self.finish('Invalid base64 encoding')
            return

        country = payload.get('country', '')
        procid = payload.get('procid', '')

        output_dir = "uploads"  
        os.makedirs(output_dir, exist_ok=True)
        file_name = os.path.join(output_dir, "uploaded_image_"+procid+".jpg")

        try:
            with open(file_name, "wb") as f:
                f.write(jpeg_bytes)
        except Exception as e:
            self.set_status(500)
            self.finish(f'Error saving image to disk: {str(e)}')
            return

        process = subprocess.Popen(
            ['/usr/bin/alpr', '-c', country, '-n', '1', '-j', file_name],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )        

        stdout, stderr = process.communicate()

        if process.returncode == 0:
            try:
                if os.path.exists(file_name):
                    os.remove(file_name)

                result = json.loads(stdout)
                self.finish(json.dumps(result))
            except json.JSONDecodeError as e:
                result = {"status":False,"error":e.msg}
                self.finish(json.dumps(result))
        else:
            result = {"status":False,"error":stderr.decode('utf-8')}
            self.finish(json.dumps(result))            

class CheckHandler(tornado.web.RequestHandler):
    def get(self):
        results = {"status": "OK"}
        self.finish(json.dumps(results))


application = tornado.web.Application([
    (r"/alpr", MainHandler),
    (r"/check", CheckHandler),
])

if __name__ == "__main__":
    application.listen(7878)
    tornado.ioloop.IOLoop.current().start()