import os
from datetime import datetime

try:
    # Create the base log directory and the dated subdirectory
    base_log_dir = "log"
    dated_log_dir = os.path.join(base_log_dir, datetime.today().strftime("%y%m%d"))

    # This will create both directories if they don't exist, and do nothing if they do
    os.makedirs(dated_log_dir, exist_ok=True)
except Exception as e:
    print(f"An error occurred: {e}")

log_file_name = datetime.today().strftime("%y%m%d_%H%M%S") + "_Log.txt"
log_full_file = dated_log_dir + "/" + log_file_name

def write_log(text):
    data_ora = datetime.now()
    if not os.path.exists(log_full_file):
        data_string = data_ora.strftime("%d/%m/%Y") + "\n"
    else:
        data_string = ""
    ora_string = data_ora.strftime("%H:%M:%S")
    with open(log_full_file, 'a') as f:
        f.write(data_string + "\n")
        f.write(ora_string + " - ")
        f.write(text)
        f.write('\n')