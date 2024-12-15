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
        cmd = f"./ns3 run 'single-bss-mld --rngRun={rng_run} --payloadSize={max_packets} --mldPerNodeLambda={lambda_val} --nMldSta={n_Stations} --simulationTime={simulation_time}'"
        subprocess.run(cmd, shell=True)


    # Analyze the results for cwmin == 16 mlo_model
    mlo_model_queuing_x = [0.003,0.006,0.009,0.012,0.015,0.018,0.021,0.024,0.027,0.03,0.033,0.036,0.039,0.0417826902931823,0.0418826902931823]
    mlo_model_queuing_y = [0.000578344525983311,0.00119522542285823,0.00185934484728125,0.00258231219003803,0.00337995477935083,0.00427440148556557,0.00529752561303441,0.00649690179516904,0.00794670405975404,0.00976907329730723,0.0121798929241376,0.0155991547495701,0.0209655654369085,0.0298997906794778,100000]
    mlo_model_access_x = [0.003,0.006,0.009,0.012,0.015,0.018,0.021,0.024,0.027,0.03,0.033,0.036,0.039,0.0417826902931823,0.0418826902931823,0.06]
    mlo_model_access_y = [0.378132948655047,0.383315823159901,0.38915441981191,0.395784034698124,0.403380717408402,0.412178208287285,0.42249428858782,0.43477342316636,0.449659146476689,0.468124439153707,0.491725029797416,0.523143724055856,0.56753900894298,0.63036636631725,8.59543638386098,8.59543638386098]
    mlo_model_e2e_x = [0.003,0.006,0.009,0.012,0.015,0.018,0.021,0.024,0.027,0.03,0.033,0.036,0.039,0.0417826902931823,0.0418826902931823]
    mlo_model_e2e_y = [0.37871129318103,0.384511048582759,0.391013764659191,0.398366346888162,0.406760672187753,0.41645260977285,0.427791814200854,0.441270324961529,0.457605850536443,0.477893512451015,0.503904922721554,0.538742878805426,0.588504574379888,0.660266156996728,100000]

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
