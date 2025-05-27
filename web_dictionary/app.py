from flask import Flask, render_template, request, jsonify
import json
from collections import defaultdict

app = Flask(__name__)

# Загрузка словаря
with open('dictionary.json', 'r', encoding='utf-8') as f:
    dictionary = json.load(f)

# Кэширование грамматических категорий
grammar_categories = {
    'POS': set(),
    'Case': set(),
    'Number': set(),
    'Gender': set()
}

for entry in dictionary:
    for category in grammar_categories:
        if entry.get(category):
            grammar_categories[category].add(entry[category])

# Преобразование в списки и сортировка
for category in grammar_categories:
    grammar_categories[category] = sorted(grammar_categories[category])

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search')
def search():
    query = request.args.get('q', '').strip().lower()
    filters = {
        'POS': request.args.get('pos'),
        'Case': request.args.get('case'),
        'Number': request.args.get('number'),
        'Gender': request.args.get('gender')
    }

    results = [
        entry for entry in dictionary
        if (not query or query in entry['Word '].strip().lower()) and
        all(not filters[cat] or entry.get(cat) == filters[cat] 
        for cat in filters)
    ]
    
    return jsonify(results)

@app.route('/grammar_categories')
def get_grammar_categories():
    return jsonify(grammar_categories)

if __name__ == '__main__':
    app.run(debug=True)