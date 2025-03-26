from .cli.command import main
from .config import load_config

load_config()
main()