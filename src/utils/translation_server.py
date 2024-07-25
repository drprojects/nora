import os
import json
import time
import psutil
import signal
import subprocess
from os.path import dirname


__all__ = ['translate_from_url', 'translate_from_identifier']
SERVER_PORT = 1969
SERVER_IP = f"http://127.0.0.1:{SERVER_PORT}"


def get_pid_using_port(port):
    """Recover the PID of the process using a given port."""
    port = int(port)
    for con in psutil.net_connections():
        if con.raddr != tuple() and con.raddr.port == port:
            return con.pid
        if con.laddr != tuple() and con.laddr.port == port:
            return con.pid
    return -1


def start_server(port=SERVER_PORT, patience=5, timestep=0.1):
    """Create a subprocess running the npm translation-server. We do not
    want to see the logs of the sever in the default console, so we
    pipe the logs elsewhere.
    """
    path = os.path.join(dirname(dirname(__file__)), 'translation_server')
    command = ['npm', 'start', '--prefix', path]
    std = subprocess.PIPE
    process = subprocess.Popen(command, stdout=std, stderr=std)
    
    # Wait for the process to have opened another subprocess listening
    # to the selected port. This makes sure we only return from this
    # function once the server is running and ready to be used
    start = time.time()
    t = 0
    pid = get_pid_using_port(port)
    while (pid is None or pid == -1) and t < patience:
        time.sleep(timestep)
        pid = get_pid_using_port(port)
        t = time.time() - start
        
    return process


def kill_server(process, port=SERVER_PORT, patience=5, timestep=0.1):
    """Kill the server and the associated process listening to port
    1969.
    """
    process.terminate()
    process.kill()
    
    pid = get_pid_using_port(port)

    if pid is None or pid == -1:
        return
    
    os.kill(get_pid_using_port(port), signal.SIGTERM)
    
    # Wait for the subprocess listening to the selected port to 
    # properly killed. This makes sure we only return from this
    # function once the server is killed
    start = time.time()
    t = 0
    pid = get_pid_using_port(port)
    
    while pid is not None and pid > -1 and t < patience:
        pid = get_pid_using_port(port)
        time.sleep(timestep)
        t = time.time() - start


def json_to_python(data):
    """Simple wrapper around json parsing in case the output of a
    program is not a json object. Also do some data cleaning to have
    something similar to what the ZoteroLibrary manipulates.
    """
    try:
        data = data.decode()
    except (UnicodeDecodeError, AttributeError):
        pass

    try:
        data = json.loads(data)
    except:
        pass

    # Raise error is the output is a string. This usually means the
    # translation server returned an error message. Typically:
    # "The remote document is not in a supported format"
    if isinstance(data, str):
        raise RuntimeError(data)

    # The returned value should be a List(Dict). If this is not the
    # case, raise an error
    if not isinstance(data, list):
        raise ValueError(f"Expected a List, got a {type(data)}")
    if not isinstance(data[0], dict):
        raise ValueError(f"Expected a List(Dict), got a List({type(data[0])})")
    data = data[0]

    # The returned json dictionary does not have exactly the same
    # structure as what is recovered when querying a ZoteroLibrary.
    # In particular, many of the keys present in the first
    # hierarchical level of the json are otherwise place under
    # another 'data' key in the ZoteroLibrary. So we manually create
    # a 'data' key under which all the keys are copied here.
    if 'data' not in data.keys():
        data['data'] = {**data}

    return data


def translate_from_url(url, timeout=20):
    """Retrieve metadata for a webpage. Returns an array of translated
    items in Zotero API JSON format. This mimics the behavior of the
    Zotero plugin for adding pages from the browser.
    """
    process = start_server()
    command = ['curl', '-d', url, '-m', f'{timeout}', '-H', "Content-Type: text/plain", f"{SERVER_IP}/web"]
    out = json_to_python(subprocess.check_output(command))
    kill_server(process)
    return out


def translate_from_identifier(identifier, timeout=20):
    """Retrieve metadata from an identifier (DOI, ISBN, PMID, arXiv ID).
    Note that for some of these identifiers, the parsed libraries may
    not provide as extensive metadata as when parsing from the web page
    with `translate_from_url`. This is typically the case when using the
    DOI: the crossref database will be used, which usually does not
    provide paper abstracts.
    """
    process = start_server()
    command = ['curl', '-d', f"{identifier}", '-m', f'{timeout}', '-H', "Content-Type: text/plain", f"{SERVER_IP}/search"]
    out = json_to_python(subprocess.check_output(command))
    kill_server(process)
    return out
