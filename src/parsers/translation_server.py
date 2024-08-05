import os
import signal
import subprocess
from src.utils.translation_server import get_pid_using_port


TRANSLATION_SERVER_PORT = 1969


# Create a subprocess running the npm translation-server
# We do not want to see the logs of the sever in the default console, so
# we pipe the logs eleswhere
process = subprocess.Popen(['npm', 'start'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

# Killing our subprocess will not entirely kill the npm server. We also
# need to kill the process using the port 1969, which is the port
# translation-server uses
process.terminate()
process.kill()
os.kill(get_pid_using_port(TRANSLATION_SERVER_PORT), signal.SIGTERM)
del process

