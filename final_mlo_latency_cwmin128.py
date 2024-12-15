# Author: Ian Li
import os
import subprocess
import shutil
import signal
import sys
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np

def control_c(signum, frame):
    print("exiting")
    sys.exit(1)

signal.signal(signal.SIGINT, control_c)

def main():
    dirname = '11be-mlo'
    ns3_path = os.path.join('../../../../ns3')
    
    # Check if the ns3 executable exists
    if not os.path.exists(ns3_path):
        print(f"Please run this program from within the correct directory.")
        sys.exit(1)

    results_dir = os.path.join(os.getcwd(), 'results', f"{dirname}-{datetime.now().strftime('%Y%m%d-%H%M%S')}")
    os.system('mkdir -p ' + results_dir)


    # Move to ns3 top-level directory
    os.chdir('../../../../')
    

    # Check for existing data files and prompt for removal
    check_and_remove('wifi-mld.dat')

    # Experiment parameters
        # Default greedy allocation (optionalTid set to false)
        # Aggregate arrival rate from 0.003 to 0.06
        # Channel width is 20 MHz
        # CWmin is [16] or 128
    rng_run = 1
    max_packets = 1500
    n_Stations = 20
    simulation_time = 60
    lambda_list = [round(val, 3) for val in np.linspace(0.003, 0.06, 20)]
    print(lambda_list)
    per_node_lambda_list = [round(i / n_Stations, 5) for i in lambda_list]
    print(per_node_lambda_list)

    # Run the ns3 simulation for each distance
    for lambda_val in per_node_lambda_list:
        print(f"Running simulation for lambda = {lambda_val}")
        cmd = (f"./ns3 run 'single-bss-mld --rngRun={rng_run} --payloadSize={max_packets} "
               f"--mldPerNodeLambda={lambda_val} --nMldSta={n_Stations} --simulationTime={simulation_time} "
               f"--acBECwminLink1=128 --acBECwminLink2=128 "
               f"--acBKCwminLink1=128 --acBKCwminLink2=128 "
               f"--acVICwminLink1=128 --acVICwminLink2=128 "
               f"--acVOCwminLink1=128 --acVOCwminLink2=128'")
        subprocess.run(cmd, shell=True)


    # Analyze the results for cwmin == 128 mlo_model
    mlo_model_queuing_x = [0.003,0.006,0.009,0.012,0.015,0.018,0.021,0.024,0.027,0.03,0.033,0.036,0.039,0.042,0.045,0.0475743567683261,0.0476743567683261]
    mlo_model_queuing_y = [0.00378053234045909,0.00833806195555142,0.013907039007457,0.0208163940760753,0.0295391255995708,0.0407752549634261,0.0555966954935917,0.0757135685913074,0.103995353363762,0.14557343046305,0.210420125692451,0.32025495676859,0.531001671321866,1.0324333350769,2.97765446329615,152.389941252501,100000]
    mlo_model_access_x = [0.003,0.006,0.009,0.012,0.015,0.018,0.021,0.024,0.027,0.03,0.033,0.036,0.039,0.042,0.045,0.0475743567683261,0.0476743567683261,0.06]
    mlo_model_access_y = [0.910079047500958,0.946539040771609,0.987629307927872,1.03430887102497,1.08782672614029,1.14984280896705,1.22261643242948,1.3093116832507,1.41451669131022,1.54518067030181,1.71243842242462,1.93554112556913,2.25162496380964,2.74600660283739,3.69452580723212,6.97309644551152,7.55122930655201,7.55122930655201]
    mlo_model_e2e_x = [0.003,0.006,0.009,0.012,0.015,0.018,0.021,0.024,0.027,0.03,0.033,0.036,0.039,0.042,0.045,0.0475743567683261,0.0476743567683261]
    mlo_model_e2e_y = [0.913859579841417,0.95487710272716,1.00153634693533,1.05512526510105,1.11736585173986,1.19061806393048,1.27821312792307,1.38502525184201,1.51851204467398,1.69075410076486,1.92285854811707,2.25579608233772,2.78262663513151,3.77843993791428,6.67218027052827,159.363037698012,100000]
    
    # draw plots
    throughput_total = []
    queuing_delay = []
    access_delay = []
    e2e_latency = []
    with open('wifi-mld.dat', 'r') as f:
        lines = f.readlines()
        for line in lines:
            tokens = line.split(',')
            throughput_total.append(float(tokens[5]))
            queuing_delay.append(float(tokens[8]))
            access_delay.append(float(tokens[11]))
            e2e_latency.append(float(tokens[14]))

    # Plot Throughput
    plt.figure()
    plt.title('Throughput vs. Offered Load')
    plt.xlabel('Offered Load')
    plt.ylabel('Throughput (Mbps)')
    plt.grid(True, axis='both', which='both')
    plt.plot(lambda_list, throughput_total, marker='o', label='ns-3 Total Throughput')
    plt.legend()
    plt.savefig(os.path.join(results_dir, 'throughput.png'))

    # Plot Queuing Delay
    plt.figure()
    plt.title('Queuing Delay vs. Offered Load')
    plt.xlabel('Offered Load')
    plt.ylabel('Queuing Delay (ms)')
    plt.grid(True, axis='both', which='both')
    plt.ylim(0, 1)
    plt.plot(lambda_list, queuing_delay, marker='o', linestyle='', label="ns-3 Queuing Delay")
    plt.plot(mlo_model_queuing_x, mlo_model_queuing_y, linestyle='--',label='model, MLO')
    plt.legend()
    plt.savefig(os.path.join(results_dir, 'queuing_delay.png'))

    # Plot Access Delay
    plt.figure()
    plt.title('Access Delay vs. Offered Load')
    plt.xlabel('Offered Load')
    plt.ylabel('Access Delay (ms)')
    plt.grid(True, axis='both', which='both')
    plt.ylim(0, 10)
    plt.plot(lambda_list, access_delay, marker='o', linestyle='', label="ns-3 Access Delay")
    plt.plot(mlo_model_access_x, mlo_model_access_y, linestyle='--', label='model, MLO')
    plt.legend()
    plt.savefig(os.path.join(results_dir, 'access_delay.png'))

    # Plot E2E Latency
    plt.figure()
    plt.title('E2E Latency vs. Offered Load')
    plt.xlabel('Offered Load $\lambda$')
    plt.ylabel('E2E Latency (ms)')
    plt.grid(True, axis='both', which='both')
    plt.ylim(0, 10)
    plt.plot(lambda_list, e2e_latency, marker='o', linestyle='', label="ns-3 E2E Latency")
    plt.plot(mlo_model_e2e_x, mlo_model_e2e_y, linestyle='--', label='model, MLO')
    plt.legend()
    plt.savefig(os.path.join(results_dir, 'e2e_latency.png'))

    # Move result files to the experiment directory
    move_file('wifi-mld.dat', results_dir)


    # Save the git commit information
    with open(os.path.join(results_dir, 'git-commit.txt'), 'w') as f:
        commit_info = subprocess.run(['git', 'show', '--name-only'], stdout=subprocess.PIPE)
        f.write(commit_info.stdout.decode())

    
def check_and_remove(filename):
    if os.path.exists(filename):
        response = input(f"Remove existing file {filename}? [Yes/No]: ").strip().lower()
        if response == 'yes':
            os.remove(filename)
            print(f"Removed {filename}")
        else:
            print("Exiting...")
            sys.exit(1)

def move_file(filename, destination_dir):
    if os.path.exists(filename):
        shutil.move(filename, destination_dir)

if __name__ == "__main__":
    main()
