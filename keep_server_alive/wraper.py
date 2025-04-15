import datetime
import subprocess

LOG_FILE = "check_timer.log"
SCRIPT_TO_RUN = "login.py"
DAYS_INTERVAL = 1  # Number of days to wait before running the script again

def get_last_run_date(log_file):
    try:
        with open(log_file, 'r') as f:
            lines = f.readlines()
            for line in reversed(lines):
                if line.startswith('['):
                    date_str = line.split(']')[0][1:]  # extract date between [ ]
                    return datetime.datetime.strptime(date_str, "%B %d, %Y").date()
    except Exception as e:
        print(f"Error reading log file: {e}")
    return None

def should_run(last_run_date):
    today = datetime.date.today()
    if last_run_date is None:
        return True
    delta = today - last_run_date
    return delta.days >= DAYS_INTERVAL

def run_script(script):
    print(f"Running {script}...")
    subprocess.run(["python", script])

if __name__ == "__main__":
    last_run = get_last_run_date(LOG_FILE)
    if should_run(last_run):
        run_script(SCRIPT_TO_RUN)
    else:
        print("Not enough days passed since last run.")
