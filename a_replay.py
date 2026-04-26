from a_replay_parts.a_core import *
from a_replay_parts.a_trainer import *
from a_replay_parts.a_rld_backend import *
from a_replay_parts.a_frontend import HTML
from a_replay_parts.a_app import *
import sys

if __name__ == "__main__":
    sys.dont_write_bytecode = True
    run_dev_server()
