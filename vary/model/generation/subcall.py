import subprocess

TIMEOUT = 15

def run_command(command, working_directory):
    """
    Calls a subprocess with the specified command.
    Throws subprocess.TimeoutExpired if the program takes more than TIMEOUT seconds.
    """
    process = subprocess.Popen(
        command, cwd=working_directory,
        stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
        close_fds=True
    )
    process.wait(timeout = TIMEOUT)

    if process is not None:
        process.kill()