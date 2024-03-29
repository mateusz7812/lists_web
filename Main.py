from multiprocessing import Process

from app import app

server = None


def run():
    global server
    server = Process(target=_run)
    server.start()


def _run():
    app.secret_key = 'super secret key'
    app.config['SESSION_TYPE'] = 'filesystem'
    app.run(host="0.0.0.0", port=80)


def terminate():
    if server:
        server.terminate()


if __name__ == "__main__":
    run()
