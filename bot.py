# Render.com va boshqa platformalar uchun kirish nuqtasi
# Bu fayl main.py ni ishga tushiradi
from main import *

if __name__ == "__main__":
    import asyncio
    import sys
    from main import main

    if sys.platform == "win32":
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        if hasattr(sys.stderr, "reconfigure"):
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")

    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        pass
