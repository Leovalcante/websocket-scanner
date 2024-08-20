import argparse
import itertools
import os

import websocket
from websocket import WebSocketTimeoutException, WebSocketBadStatusException


def printv(msg, v_level=1):
    if v_level <= verbose_level:
        print(msg)


default_ports = [80, 443]
schemas = ["ws", "wss"]
verbose_level = 0

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="WebSocket Scanner",
        description="Scan the target(s) for websocket server",
        epilog="Scan responsibly",
    )
    parser.add_argument("-l", metavar="target", help="single target to scan")
    parser.add_argument("-L", metavar="file", help="target list")
    parser.add_argument("-p", metavar="ports", help="port list comma separated")
    parser.add_argument("--verbose", "-v", action="count", default=0)

    args = parser.parse_args()
    cmd_target = args.l
    cmd_targets = args.L
    cmd_ports = args.p
    verbose_level = args.verbose

    if not (bool(cmd_target) ^ bool(cmd_targets)):
        parser.error("ONE target is required. Specify -l or -L")

    if cmd_ports:
        fports = filter(None, cmd_ports.split(","))
        ports = []
        for p in fports:
            try:
                ports.append(int(p))
            except ValueError:
                pass
    else:
        ports = default_ports

    if cmd_target:
        targets = [cmd_target]
    else:
        if not (os.path.isfile(cmd_targets) and os.access(cmd_targets, os.R_OK)):
            raise argparse.ArgumentError(
                argument="-L", message="Target file should exists and be readable"
            )

        with open(cmd_targets) as ts:
            targets = list(map(lambda t: t.strip(), ts.readlines()))

    for schema, target, port in itertools.product(schemas, targets, ports):
        conn = f"{schema}://{target}:{port}"
        printv(f"Connection: {conn}", 2)
        try:
            ws = websocket.WebSocket()
            ws.connect(conn, timeout=3)
            print(f"{conn} ok")
        except ConnectionRefusedError:
            print(f"{conn} KO")
        except WebSocketTimeoutException:
            print(f"{conn} Timed out")
        except WebSocketBadStatusException:
            print(f"{conn} Handshake failed")
        except Exception as ex:
            print(f"{conn} Error", end=" - ")
            printv(ex)
        finally:
            if ws:
                ws.close()
