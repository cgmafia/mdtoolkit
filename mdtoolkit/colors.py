"""ANSI colour constants and print helpers."""

R   = "\033[0;31m"
G   = "\033[0;32m"
Y   = "\033[0;33m"
B   = "\033[0;34m"
C   = "\033[0;36m"
W   = "\033[1;37m"
M   = "\033[0;35m"
DIM = "\033[2m"
RST = "\033[0m"


def info(msg):  print("  " + C + "ℹ  " + RST + str(msg))
def ok(msg):    print("  " + G + "✔  " + RST + str(msg))
def warn(msg):  print("  " + Y + "⚠  " + RST + str(msg))
def err(msg):   print("  " + R + "✖  " + RST + str(msg))
def head(msg):  print("\n" + W + str(msg) + RST + "\n" + "─" * 52)
def dim(msg):   print("  " + DIM + str(msg) + RST)
def step(msg):  print("  " + M + "▶  " + RST + str(msg))


def banner(version: str = "1.0.0"):
    print(B + "╔══════════════════════════════════════════════════════════╗")
    print("║  " + W + "📄  M A R K D O W N   T O O L K I T  v" + version + B + "           ║")
    print("║  " + DIM + "Parse • Extract Code • Export Tables • PDF • GitHub" + B + "     ║")
    print("║  " + DIM + "Author: Anand Venkataraman <vand3dup@gmail.com>" + B + "         ║")
    print("╚══════════════════════════════════════════════════════════╝" + RST)
    print()
