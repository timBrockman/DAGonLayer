import asyncio

from stateguard.main import main as async_main


def run() -> int:
    return asyncio.run(async_main())


if __name__ == "__main__":
    raise SystemExit(run())
