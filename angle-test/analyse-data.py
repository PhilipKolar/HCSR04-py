import os


def get_file_names():
    import argparse
    parser = argparse.ArgumentParser(description='Analyses results from usonic.py files and stores the results in a '
                                                 'directory named \'analysis\', placed in the same directory as each '
                                                 'respective file.')
    parser.add_argument('statsFile', nargs='*')
    args = parser.parse_args()
    return args.statsFile


def get_statistics_data(filename):
    data_list = [line.strip() for line in open(filename)]
    return data_list


def remove_timeouts(data):
    no_timeouts = []
    for i in data:
        if i >= 0.0:
            no_timeouts.append(i)
    return no_timeouts


def get_quartiles(data):  # Returns value of quartile 1, median, and quartile 3 in a list, followed by their indicies.
                          # Indicies for quartiles are 1-based, data is still 0-based.
    if len(data) == 1:
        return [data[0], data[0], data[0], 1, 1, 1]

    if len(data) % 2 == 1:  # Data count odd, median points at a number
        median_index = (len(data) + 1) / 2
        median = data[median_index - 1]
        if median_index % 2 == 1:  # Median index odd, q1/q3 point between numbers
            q1_index = (median_index + 1) / 2 - 0.5
            q3_index = q1_index + median_index
            q1 = (data[int(q1_index - 0.5) - 1] + data[int(q1_index + 0.5) - 1]) / 2.0
            q3 = (data[int(q3_index - 0.5) - 1] + data[int(q3_index + 0.5) - 1]) / 2.0
        else:  # Median index even, q1/q3 point at numbers
            q1_index = median_index / 2
            q3_index = q1_index + median_index
            q1 = data[int(q1_index) - 1]
            q3 = data[int(q3_index) - 1]
    else:  # Data count even, median points between two numbers
        median_index = (float(len(data)) + 1.0) / 2.0
        median = (data[int(median_index - 0.5) - 1] + data[int(median_index + 0.5) - 1]) / 2.0

        q1_index = median_index - float(len(data)) / 4
        q3_index = median_index + float(len(data)) / 4
        if q1_index % 1 == 0:  # q1 and q3 point at a number
            q1 = data[int(q1_index) - 1]
            q3 = data[int(q3_index) - 1]
        else:  # q1 and q3 point between two numbers
            q1 = (data[int(q1_index - 0.5) - 1] + data[int(q1_index + 0.5) - 1]) / 2.0
            q3 = (data[int(q3_index - 0.5) - 1] + data[int(q3_index + 0.5) - 1]) / 2.0
    return [q1, median, q3, q1_index, median_index, q3_index]


def remove_outliers(data):
    quartiles = get_quartiles(data)
    lower_fence = quartiles[0] - 1.5 * (quartiles[2] - quartiles[0])  # = q1 - 1.5 * IQR
    upper_fence = quartiles[2] + 1.5 * (quartiles[2] - quartiles[0])  # = q3 + 1.5 * IQR
    no_outliers = []
    for i in data:
        if (i >= lower_fence) and (i <= upper_fence):
            no_outliers.append(i)
    return no_outliers


def get_mean(data):
    total = 0.0
    for i in data:
        total += i
    return total / float(len(data))


def get_standard_deviation(data):
    if len(data) == 1:
        return 0

    from math import sqrt
    mean = get_mean(data)
    sum_of = 0
    for i in data:
        sum_of += (i - mean) ** 2
    return sqrt(sum_of / (len(data) - 1))


def record_statistics(actual_distance, data, data_no_timeouts, data_no_outliers, file_name):
    f = open(file_name, 'w')
    if len(data_no_timeouts) != 0:
        quartiles = get_quartiles(data_no_timeouts)

    f.write("Actual distance:           {0:.2f}cm\n".format(actual_distance))
    f.write("Data count (w/ timeouts):  {0}\n".format(len(data)))
    f.write("Data count (w/o timeouts): {0}\n".format(len(data_no_timeouts)))
    f.write("Timeouts:                  {0}\n".format(len(data) - len(data_no_timeouts)))
    f.write("Timeout frequency:         {0:.2f}%\n".format(float(len(data) - len(data_no_timeouts)) * 100 / float(len(data))))
    if len(data_no_timeouts) != 0:
        f.write("Median:                    {0:.2f}cm\n".format(quartiles[1]))
        f.write("Mean:                      {0:.2f}cm\n".format(get_mean(data_no_timeouts)))
        f.write("Outlier Count:             {0}\n".format(len(data_no_timeouts) - len(data_no_outliers)))
        f.write("Standard deviation:        {0:.2f}cm\n".format(get_standard_deviation(data_no_timeouts)))
        f.write("Quartile 1:                {0:.2f}cm\n".format(quartiles[0]))
        f.write("Quartile 3:                {0:.2f}cm\n".format(quartiles[2]))
        f.write("Min value (w/ outliers):   {0:.2f}cm\n".format(min(data_no_timeouts)))
        f.write("Max value (w/ outliers):   {0:.2f}cm\n".format(max(data_no_timeouts)))
        f.write("Min value (w/o outliers):  {0:.2f}cm\n".format(min(data_no_outliers)))
        f.write("Max value (w/o outliers):  {0:.2f}cm\n".format(max(data_no_outliers)))
        outliers = data_no_timeouts[::]  # Copy by value
        for record in data_no_outliers:
            outliers.remove(record)
        for i in range(0, len(outliers)):
            outliers[i] = float("{0:.2f}".format(outliers[i]))
        f.write("Outliers: {0}".format(outliers))

    f.close()


def data_analysis_iteration(statistics_file):
    new_dir = os.path.dirname(statistics_file) + "." + os.sep + "analysis"
    if not os.path.exists(new_dir):
        os.makedirs(new_dir)
    file_to_write = new_dir + os.sep + "analysis-" + os.path.basename(statistics_file)

    try:
        data = get_statistics_data(statistics_file)
        if data[0][0] is not 'A' and data[0][0] is not 'a':
            print("No actual distance found in file '{0}'. Please add one.".format(statistics_file))
            return
        actual_distance = float(data.pop(0)[1:])  # Get rid of actual distance flag when retrieving value
        data = [float(i) for i in data]  # Convert all strings in the list to floats
    except:
        print("Error processing the contents of the file '{0}'. Make sure numbers are separated by newlines only".
              format(statistics_file))
        return 1

    data_no_timeouts = remove_timeouts(data)
    data_no_timeouts.sort()
    if len(data_no_timeouts) != 0:
        data_no_outliers = remove_outliers(data_no_timeouts)
    else:
        data_no_outliers = data_no_timeouts

    record_statistics(actual_distance, data, data_no_timeouts, data_no_outliers, file_to_write)


def main():
    import glob

    statistics_file_list = get_file_names()
    for statistics_file in statistics_file_list:
        if os.path.isdir(statistics_file):
            for curr_file in glob.glob(os.path.dirname(statistics_file + os.sep) + os.sep + "*.txt"):
                print("Working on {0}".format(curr_file))
                data_analysis_iteration(curr_file)
        else:
            print("Working on {0}".format(statistics_file))
            data_analysis_iteration(statistics_file)



main()