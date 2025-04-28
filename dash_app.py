from dash import Dash, dcc, html, Input, Output, State, callback_context, ALL
import dash_bootstrap_components as dbc
import pandas as pd
import csv
import re
import os

# python dash_app.py
# Load questions
base = os.getcwd()

file = r"domainQuestions\domain_Domain 1_ SDLC Automation11.csv"
file_path = os.path.join(base, file)

# Function to parse questions
def parse_questions_from_csv(file_path):
    questions = []
    with open(file_path, mode='r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            question_text, options = extract_question_and_options(row["question"])
            question_entry = {
                "question": question_text.strip(),
                "options": options,
                "answer": row["answer"].strip(),  # e.g., "AB", "D", "BDF"
            }
            questions.append(question_entry)
    return questions

# Helper to extract question and options
def extract_question_and_options(text):
    match = re.split(r'\n(?=[A-E]\.)', text, maxsplit=1)
    if len(match) == 2:
        question_part = match[0]
        options_part = match[1]
    else:
        question_part = text
        options_part = ""

    options = re.findall(r'([A-E]\..*?)(?=\n[A-E]\.|$)', options_part, re.DOTALL)
    return question_part, options

# Initialize Dash app with a premium theme
app = Dash(__name__, external_stylesheets=[
    dbc.themes.LUX,  # Lux theme for a premium look
    "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css",  # Font Awesome icons
    "https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700&display=swap"  # Google Font
])

# Custom CSS
CUSTOM_CSS = {
    'custom-card': {
        'borderRadius': '10px',
        'boxShadow': '0 4px 20px 0 rgba(0,0,0,0.12)',
        'transition': 'transform 0.3s ease, box-shadow 0.3s ease',
        'border': 'none',
        'marginBottom': '20px',
        'overflow': 'hidden',
        'background': 'linear-gradient(145deg, #ffffff, #f8f9fa)'
    },
    'custom-card:hover': {
        'transform': 'translateY(-5px)',
        'boxShadow': '0 8px 25px 0 rgba(0,0,0,0.15)'
    },
    'timer': {
        'fontSize': '18px',
        'fontWeight': '600',
        'color': '#ffffff',
        'background': 'linear-gradient(135deg, #6a11cb 0%, #2575fc 100%)',
        'padding': '10px 20px',
        'borderRadius': '50px',
        'display': 'inline-block',
        'boxShadow': '0 4px 15px rgba(106, 17, 203, 0.3)'
    },
    'question-text': {
        'fontSize': '20px',
        'fontWeight': '500',
        'color': '#2c3e50',
        'margin': '25px 0',
        'lineHeight': '1.5'
    },
    'option-item': {
        'padding': '15px',
        'margin': '8px 0',
        'borderRadius': '8px',
        'border': '1px solid #e0e0e0',
        'cursor': 'pointer',
        'transition': 'all 0.3s ease',
        'background': '#ffffff'
    },
    'option-item:hover': {
        'background': '#f8f9fa',
        'borderColor': '#2575fc'
    },
    'option-item-selected': {
        'background': 'rgba(37, 117, 252, 0.1)',
        'borderColor': '#2575fc',
        'boxShadow': '0 0 0 2px rgba(37, 117, 252, 0.2)'
    },
    'nav-button': {
        'padding': '12px 25px',
        'fontWeight': '600',
        'borderRadius': '8px',
        'transition': 'all 0.3s ease',
        'boxShadow': '0 2px 10px rgba(0,0,0,0.1)'
    },
    'submit-button': {
        'background': 'linear-gradient(135deg, #4CAF50 0%, #2E7D32 100%)',
        'border': 'none',
        'padding': '12px 30px',
        'fontWeight': '600'
    },
    'header': {
        'background': 'linear-gradient(135deg, #6a11cb 0%, #2575fc 100%)',
        'color': 'white',
        'padding': '25px 0',
        'marginBottom': '30px',
        'boxShadow': '0 4px 20px rgba(0,0,0,0.1)'
    },
    'progress-bar': {
        'height': '8px',
        'borderRadius': '4px',
        'background': '#e0e0e0',
        'marginBottom': '30px'
    },
    'progress-fill': {
        'height': '100%',
        'borderRadius': '4px',
        'background': 'linear-gradient(90deg, #6a11cb 0%, #2575fc 100%)',
        'transition': 'width 0.5s ease'
    },
    'result-item': {
        'padding': '12px 15px',
        'marginBottom': '8px',
        'borderRadius': '6px',
        'background': '#f8f9fa'
    }
}


questions = parse_questions_from_csv(file_path)

# App layout
app.layout = dbc.Container([
    # Header with gradient
    html.Div([
        dbc.Container([
            dbc.Row([
                dbc.Col([
                    html.H1("DEVOPS Certification Exam", className="display-4 mb-3", style={
                        'fontWeight': '700',
                        'textShadow': '1px 1px 3px rgba(0,0,0,0.2)'
                    }),
                    html.Div([
                        html.Span([
                            html.I(className="fas fa-clock me-2"),
                            html.Span(id="timer", style=CUSTOM_CSS['timer'])
                        ]),
                        html.Span([
                            html.I(className="fas fa-question-circle me-2 ms-4"),
                            html.Span(id="question-counter", style={
                                'fontSize': '18px',
                                'fontWeight': '600',
                                'color': '#ffffff'
                            })
                        ])
                    ])
                ], width=12)
            ])
        ], fluid=True)
    ], style=CUSTOM_CSS['header']),
    
    # Main content
    dbc.Container([
        # Progress bar
        html.Div([
            html.Div(id="progress-fill", style=CUSTOM_CSS['progress-fill'])
        ], style=CUSTOM_CSS['progress-bar']),
        
        # Question card
        dbc.Card([
            dbc.CardBody([
                html.Div(id="question-text", style=CUSTOM_CSS['question-text']),
                html.Div(id="options-container", style={'margin': '20px 0'})
            ])
        ], style=CUSTOM_CSS['custom-card'], className="mb-4"),
        
        # Navigation buttons
        dbc.Row([
            dbc.Col(dbc.Button(
                [html.I(className="fas fa-arrow-left me-2"), "Previous"],
                id="prev-btn",
                color="secondary",
                className="me-2",
                style=CUSTOM_CSS['nav-button']
            ), width="auto"),
            
            dbc.Col(dbc.Button(
                [html.I(className="fas fa-arrow-right me-2"), "Next"],
                id="next-btn",
                color="primary",
                className="me-2",
                style=CUSTOM_CSS['nav-button']
            ), width="auto"),
            
            dbc.Col(dbc.Button(
                [html.I(className="fas fa-paper-plane me-2"), "Submit Exam"],
                id="submit-btn",
                color="success",
                style=CUSTOM_CSS['submit-button']
            ), width="auto", className="ms-auto")
        ], className="mb-5", justify="start"),
        
        # Results section
        html.Div(id="results", className="mt-4")
    ], fluid=True, style={'padding': '0 20px'}),
    
    # Hidden stores
    dcc.Interval(id='interval', interval=1000, n_intervals=0),
    dcc.Store(id='current-index', data=0),
    dcc.Store(id='answers', data={}),
    
    # Custom CSS
    html.Div(
        dcc.Markdown("""
        <style>
            body {{
                font-family: 'Montserrat', sans-serif;
                background-color: #f5f7fa;
            }}
            .card {{
                {custom_card_style}
            }}
            .card:hover {{
                {custom_card_hover_style}
            }}
        </style>
        """.format(
            custom_card_style='; '.join([f'{k}: {v}' for k, v in CUSTOM_CSS['custom-card'].items()]),
            custom_card_hover_style='; '.join([f'{k}: {v}' for k, v in CUSTOM_CSS['custom-card:hover'].items()])
        ), 
        dangerously_allow_html=True
    ))
], fluid=True, style={'minHeight': '100vh'})

# Timer callback
def format_time(n, total_time):
    time_left = max(total_time - n, 0)
    mins, secs = divmod(time_left, 60)
    return f"{mins:02d}:{secs:02d}"

@app.callback(
    Output("timer", "children"),
    Input("interval", "n_intervals")
)
def update_timer(n):
    total_time = 3 * len(questions) * 60  # 3 times the number of questions in minutes
    return format_time(n, total_time)

# Update question counter
@app.callback(
    Output("question-counter", "children"),
    Input("current-index", "data")
)
def update_question_counter(index):
    return f"Question {index + 1} of {len(questions)}"

# Update progress bar
@app.callback(
    Output("progress-fill", "style"),
    Input("current-index", "data")
)
def update_progress(index):
    progress = (index + 1) / len(questions) * 100
    style = CUSTOM_CSS['progress-fill'].copy()
    style['width'] = f"{progress}%"
    return style

# Callback to load question
@app.callback(
    Output('question-text', 'children'),
    Output('options-container', 'children'),
    Output('prev-btn', 'disabled'),
    Output('next-btn', 'disabled'),
    Input('current-index', 'data'),
    Input('answers', 'data')
)
def display_question(index, answers):
    q = questions[index]
    selected = answers.get(str(index), [])
    
    # Create option items with custom styling
    options = []
    for i, opt in enumerate(q['options']):
        is_selected = opt[0] in selected
        option_style = CUSTOM_CSS['option-item'].copy()
        if is_selected:
            option_style.update(CUSTOM_CSS['option-item-selected'])
        
        options.append(
            html.Label([
                dcc.Checklist(
                    options=[{'label': '', 'value': opt[0]}],
                    value=[opt[0]] if is_selected else [],
                    id={'type': 'option', 'index': f'{index}-{i}'},
                    inputClassName="me-2",
                    style={'display': 'inline-block'}
                ),
                html.Span(opt, style={'verticalAlign': 'middle'})
            ], 
            style=option_style,
            className="d-flex align-items-center"
        ))
    
    return (
        f"Q{index + 1}: {q['question']}",
        options,
        index == 0,
        index == len(questions) - 1
    )

# Callback to handle option selection
@app.callback(
    Output('answers', 'data'),
    Input({'type': 'option', 'index': ALL}, 'value'),
    State('current-index', 'data'),
    State('answers', 'data'),
    prevent_initial_call=True
)
def update_answers(option_values, index, answers):
    # Get the context to see which input was triggered
    ctx = callback_context
    if not ctx.triggered:
        return answers
    
    # Get all selected options for current question
    selected = []
    for val in option_values:
        if val:  # If option is selected
            selected.extend(val)
    
    answers[str(index)] = selected
    return answers

# Callback to store answers and navigate
@app.callback(
    Output('current-index', 'data'),
    Input('prev-btn', 'n_clicks'),
    Input('next-btn', 'n_clicks'),
    State('current-index', 'data'),
    State('answers', 'data'),
    prevent_initial_call=True
)
def navigate(prev_clicks, next_clicks, index, answers):
    ctx = callback_context
    if not ctx.triggered:
        return index
    
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    if button_id == 'next-btn' and index < len(questions) - 1:
        index += 1
    elif button_id == 'prev-btn' and index > 0:
        index -= 1
    return index

# Submit callback
@app.callback(
    Output('results', 'children'),
    Input('submit-btn', 'n_clicks'),
    State('answers', 'data'),
    prevent_initial_call=True
)
def show_results(n_clicks, answers):
    if not n_clicks:
        return ''
    
    score = 0
    details = []
    
    for i, q in enumerate(questions):
        ans = answers.get(str(i), [])
        correct = q['answer']
        correct_set = set(correct)
        ans_set = set(ans)
        is_correct = (ans_set == correct_set)
        
        if is_correct:
            score += 1
            
        details.append(html.Div([
            html.Div([
                html.Span(f"Q{i+1}: ", style={'fontWeight': '600'}),
                html.Span(f"Your answer: {''.join(sorted(ans)) if ans else 'No answer'}"),
                html.Span(" • ", style={'color': '#999'}),
                html.Span(f"Correct: {correct}", style={'color': '#4CAF50' if is_correct else '#F44336'}),
                html.Span(" • ", style={'color': '#999'}),
            ], style=CUSTOM_CSS['result-item'])
        ]))
    
    percentage = (score / len(questions)) * 100
    result_color = '#4CAF50' if percentage >= 70 else '#F44336'
    
    return dbc.Card([
        dbc.CardBody([
            html.H3("Exam Results", className="mb-4", style={'color': '#2c3e50'}),
            html.Div([
                html.Div([
                    html.Div([
                        html.Div(f"{percentage:.0f}%", style={
                            'fontSize': '48px',
                            'fontWeight': '700',
                            'color': result_color
                        }),
                        html.Div(f"{score} out of {len(questions)} correct", style={
                            'fontSize': '18px',
                            'color': '#666'
                        })
                    ], style={'textAlign': 'center'})
                ], className="mb-4"),
                
                html.Div([
                    html.H5("Detailed Results", className="mb-3"),
                    html.Div(details)
                ])
            ])
        ])
    ], style=CUSTOM_CSS['custom-card'])

if __name__ == '__main__':
    app.run(debug=True)