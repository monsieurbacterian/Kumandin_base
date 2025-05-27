from flask import render_template, request
import pandas as pd
import re
from app import app

CSV_PATH = r'C:\Users\User\Desktop\Диссертация\Диссер_и_список литры\веб-корпус 1.2\tails_corpora.csv'

# Загрузка данных с проверкой
try:
    df = pd.read_csv(CSV_PATH)
    # Проверяем наличие нужных колонок
    required_columns = ['Name', 'Sent_kum', 'Sent_rus', 'Text_kum', 'Text_rus']
    if not all(col in df.columns for col in required_columns):
        missing = [col for col in required_columns if col not in df.columns]
        raise ValueError(f"Отсутствуют колонки: {', '.join(missing)}")
except Exception as e:
    print(f"Ошибка загрузки CSV: {str(e)}")
    df = pd.DataFrame(columns=required_columns)

def highlight(text, query):
    """Подсвечивает все вхождения запроса в тексте"""
    if pd.isna(text) or not query:
        return text
    return re.sub(f'({re.escape(query)})', 
                r'<span class="highlight">\1</span>', 
                str(text), 
                flags=re.IGNORECASE)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('q', '').strip()
    if not query:
        return render_template('index.html', error="Введите поисковый запрос")

    try:
        # Ищем только в русских предложениях (Sent_rus)
        mask = df['Sent_rus'].str.contains(query, case=False, na=False)
        results = df[mask].copy()
        
        # Подсвечиваем найденные слова в русских текстах
        results['Sent_rus_hl'] = results['Sent_rus'].apply(lambda x: highlight(x, query))
        results['Text_rus_hl'] = results['Text_rus'].apply(lambda x: highlight(x, query))
        
        # Формируем список результатов
        output = []
        for _, row in results.iterrows():
            output.append({
                'name': row['Name'],
                'rus_sent': row['Sent_rus_hl'],
                'kum_sent': row['Sent_kum'],
                'rus_text': row['Text_rus_hl'],
                'kum_text': row['Text_kum']
            })
        
        return render_template('results.html',
                            query=query,
                            results=output)
    
    except Exception as e:
        print(f"Ошибка поиска: {str(e)}")
        return render_template('index.html', 
                            error="Ошибка при выполнении поиска. Проверьте данные.")