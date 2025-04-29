
from flask import Flask, render_template, request, redirect, url_for
import random
import matplotlib.pyplot as plt
import os

app = Flask(__name__)
results = []

def generate_gantt_chart(jobs):
    fig, gnt = plt.subplots(figsize=(10, 5))
    gnt.set_xlabel('Time')
    gnt.set_ylabel('Jobs')
    gnt.set_yticks([15 + i * 10 for i in range(len(jobs))])
    gnt.set_yticklabels([job['name'] for job in jobs])
    gnt.grid(True)

    start_time = 0
    for i, job in enumerate(jobs):
        gnt.broken_barh([(start_time, job['burst_time'])], (10 + i * 10, 9), facecolors='tab:blue')
        job['completion_time'] = start_time + job['burst_time']
        start_time += job['burst_time']

    plt.tight_layout()
    plt.savefig(os.path.join("static", "gantt_chart.png"))
    plt.close()

def generate_line_graph(jobs):
    job_names = [job['name'] for job in jobs]
    completion_times = [job['completion_time'] for job in jobs]

    plt.figure(figsize=(10, 5))
    plt.plot(job_names, completion_times, marker='o', linestyle='-', color='green')
    plt.title("Job Completion Times")
    plt.xlabel("Jobs")
    plt.ylabel("Completion Time")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(os.path.join("static", "line_graph.png"))
    plt.close()

@app.route('/')
def welcome():
    return render_template('welcome.html')

@app.route('/book', methods=['GET', 'POST'])
def book():
    global results
    if request.method == 'POST':
        passengers = []
        names = request.form.getlist('name')
        classes = request.form.getlist('class')
        tickets = request.form.getlist('tickets')
        algorithms = request.form.getlist('algorithm')

        for name, cls, ticket_count, algo in zip(names, classes, tickets, algorithms):
            for i in range(int(ticket_count)):
                passengers.append({
                    'name': f"{name}_{i+1} ({cls})",
                    'burst_time': random.randint(1, 5),
                    'algorithm': algo
                })


        # Prioritize Business class first
        business = [p for p in passengers if '(Business)' in p['name']]
        economy = [p for p in passengers if '(Economy)' in p['name']]

        # Apply algorithm-specific sort inside each class
        def sort_by_algo(passenger_list):
            sorted_list = []
            rr_time_quantum = 2
            for algo in ['FCFS', 'SJF', 'Priority', 'Round Robin']:
                temp = [p for p in passenger_list if p['algorithm'] == algo]
                if algo == 'SJF':
                    temp.sort(key=lambda x: x['burst_time'])
                elif algo == 'Priority':
                    for p in temp:
                        p['priority'] = random.randint(1, 10)
                    temp.sort(key=lambda x: x['priority'])
                elif algo == 'Round Robin':
                    temp.sort(key=lambda x: x['name'])  # Keep order for RR; actual implementation can be more advanced
                sorted_list.extend(temp)
            return sorted_list

        business_sorted = sort_by_algo(business)
        economy_sorted = sort_by_algo(economy)
        passengers = business_sorted + economy_sorted

        generate_gantt_chart(passengers)
        generate_line_graph(passengers)
        results = passengers

        return redirect(url_for('result'))

    return render_template('book.html')

@app.route('/result')
def result():
    return render_template('result.html', jobs=results)

if __name__ == '__main__':
    app.run(debug=True)
