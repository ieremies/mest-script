import sys
import yaml
import numpy as np
import matplotlib.pyplot as plt


def get_common_instances(files):
    common_instances = None

    for file_path in files:
        with open(file_path, "r") as file:
            data = yaml.load(file, Loader=yaml.FullLoader)
            current_instances = set(data.keys())

            if common_instances is None:
                common_instances = current_instances
            else:
                common_instances = common_instances.intersection(current_instances)

    return common_instances


def get_times(data, instances):
    times = [data[k]["run_time"] for k in instances if data[k]["run_time"] is not None]
    return times


def plot_cumulative_times(times, label):
    times = np.array(times)
    times.sort()
    y = np.arange(len(times)) / len(times)
    plt.xscale("log")
    plt.xlabel("Time (s)")
    plt.xlim(0.001, max(times))

    plt.ylabel("Cumulative probability")
    plt.ylim(0.0, 1.0)
    plt.grid(True)
    plt.plot(times, y, label=label)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python script.py file1.yaml file2.yaml ...")
        sys.exit(1)

    files = sys.argv[1:]
    common_instances = get_common_instances(files)
    print(*common_instances, sep="\n")
    print(f"Using data from {len(common_instances)} common instances.")

    plt.figure(figsize=(10, 6))  # Adjust the figure size if needed

    for file_path in files:
        with open(file_path, "r") as file:
            data = yaml.load(file, Loader=yaml.FullLoader)
            times = get_times(data, common_instances)
            # print sum of times
            print(f"Total time for {file_path}: {sum(times)}")
            plot_cumulative_times(times, label=f"File {file_path}")

    plt.legend()
    plt.show()
