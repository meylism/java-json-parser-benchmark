import plotly.graph_objects as go
import plotly.io as pio
from plotly.subplots import make_subplots
import numpy as np
import re
import os

CSV_HOME = "output/csv"
OUTPUT_HOME = "../../charts"
SET_SIZES_AS_X = True

def draw_ser_and_deser(ser, deser, title):
    sizes = parse_title(ser)
    scores, errors, libraries = parse_scores(ser)
    colors = ['#577590', '#f8961e', '#f94144', '#f9844a', '#277da1', 
              '#f9c74f', '#90be6d', '#43aa8b', '#4d908e', '#f3722c']

    fig = make_subplots(rows=2, 
                        cols=1, 
                        shared_xaxes=True, 
                        subplot_titles=("Serialization", "Deserialization"), 
                        y_title="ops/s")

    if SET_SIZES_AS_X:
        x = sizes
        name = libraries
    else:
        x = libraries
        name = sizes

    for i in range(len(scores)):
        fig.add_trace(go.Bar(name=name[i],
                             x=x,
                             y=scores[i],
                             error_y=dict(type='data', array=errors[i]),
                             legendgroup="group", 
                             marker=dict(color=colors[i])),
                      row=1, 
                      col=1)
        
    sizes = parse_title(deser)
    scores, errors, libraries = parse_scores(deser)

    if SET_SIZES_AS_X:
        x = sizes
        name = libraries
    else:
        x = libraries
        name = sizes

    for i in range(len(scores)):
        fig.add_trace(go.Bar(name=name[i],
                             x=x,
                             y=scores[i],
                             error_y=dict(type='data', array=errors[i]),
                             legendgroup="group", 
                             marker=dict(color=colors[i]), 
                             showlegend=False), 
                      row=2, 
                      col=1)

    fig.update_layout(
        title=data_type.capitalize(),
        xaxis_tickfont_size=14,
        yaxis=dict(
            titlefont_size=16,
            tickfont_size=14,
        ),
        barmode='group',
        bargap=0.2, # gap between bars of adjacent location coordinates.
        bargroupgap=0.15 # gap between bars of the same location coordinate.
    )
    
    if not os.path.exists(OUTPUT_HOME):
        os.mkdir(OUTPUT_HOME)
    pio.kaleido.scope.default_format = "webp"
    fig.write_image("{}/{}.webp".format(OUTPUT_HOME, data_type), scale=1)

# Returns: scores, errors, libraries
def parse_scores(lines):
    stats = lines[1:]
    libraries = []
    scores = []
    scores_err = []

    for stat in stats:
        split_stat = stat.strip().split(',')
        libraries.append(split_stat[0])
        temp_scores = []
        temp_err = []

        for raw_score in split_stat[1:]:
            score, err = raw_score.split('±')
            temp_scores.append(round(float(score), 1))
            temp_err.append(round(float(err), 1))
        scores.append(temp_scores)
        scores_err.append(temp_err)

    if SET_SIZES_AS_X:
        return scores, scores_err, libraries
    return np.transpose(scores).tolist(), np.transpose(scores_err).tolist(), libraries

# Returns: sizes
def parse_title(lines):
    title = lines[0]
    sizes = title.split(',')[1:]
    
    for size in sizes:
        result = re.findall('\\d+', size)

    return sizes

serde = {"ser": "deser", "deser": "ser"}
os.chdir(CSV_HOME)
cwd = os.getcwd()
csv_files = os.listdir(cwd)
r = re.compile(".+-.+-.+\\.csv$")
csv_files = list(filter(r.match, csv_files))

while len(csv_files) > 0:
    file_details = csv_files[0].split('.')[0].split('-')
    another_file = "{}-{}-{}.csv".format(file_details[0], serde[file_details[1]], file_details[2])
    data_type = file_details[0]
    
    if another_file in csv_files:
        
        if file_details[1] == "ser":
            ser = csv_files[0]
            deser = another_file
        else:
            ser = another_file
            deser = csv_files[0]
        
        with open(ser) as f1, open(deser) as f2:
            draw_ser_and_deser(f1.readlines(), f2.readlines(), data_type)
        
        csv_files.remove(ser)
        csv_files.remove(deser)