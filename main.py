from multiprocessing import Process

from app import app

server = None


def run():
    global server
    server = Process(target=_run)
    server.start()


def _run():
    app.run()


def terminate():
    if server:
        server.terminate()


if __name__ == "__main__":
    run()
