from flask import Flask, render_template, request
from collections import defaultdict
import re

app = Flask(__name__)

# Список стоп-слов
stop_words = set(['и', 'в', 'во', 'не', 'что', 'он', 'на', 'я', 'с', 'со', 'как', 'а', 'то', 'все', 'она', 'так', 'его', 'но', 'да', 'ты', 'к', 'у', 'же', 'вы', 'за', 'бы', 'по', 'только', 'ее', 'мне', 'было', 'вот', 'от', 'меня', 'еще', 'нет', 'о', 'из', 'ему', 'теперь', 'когда', 'даже', 'ну', 'вдруг', 'ли', 'если', 'уже', 'или', 'ни', 'быть', 'был', 'него', 'до', 'вас', 'нибудь', 'опять', 'уж', 'вам', 'ведь', 'там', 'потом', 'себя', 'ничего', 'ей', 'может', 'они', 'тут', 'где', 'есть', 'надо', 'ней', 'для', 'мы', 'тебя', 'их', 'чем', 'была', 'сам', 'чтоб', 'без', 'будто', 'чего', 'раз', 'тоже', 'себе', 'под', 'будет', 'ж', 'тогда', 'кто', 'этот', 'того', 'потому', 'этого', 'какой', 'совсем', 'ним', 'здесь', 'этом', 'один', 'почти', 'мой', 'тем', 'чтобы', 'нее', 'сейчас', 'были', 'куда', 'зачем', 'всех', 'никогда', 'можно', 'при', 'наконец', 'два', 'об', 'другой', 'хоть', 'после', 'над', 'больше', 'тот', 'через', 'эти', 'нас', 'про', 'всего', 'них', 'какая', 'много', 'разве', 'три', 'эту', 'моя', 'впрочем', 'хорошо', 'свою', 'этой', 'перед', 'иногда', 'лучше', 'чуть', 'том', 'нельзя', 'такой', 'им', 'более', 'всегда', 'конечно', 'всю', 'между'])

def simple_stem(word):
    """Простой стеммер для русского языка"""
    suffixes = ['ов', 'ев', 'ив', 'ый', 'ий', 'ая', 'яя', 'ое', 'ее', 'ые', 'ие', 'ым', 'им', 'ыми', 'ими',
                'ей', 'ой', 'ей', 'ой', 'ем', 'им', 'ам', 'ям', 'ом', 'ах', 'ях', 'ую', 'юю', 'у', 'ю',
                'а', 'я', 'о', 'е', 'ь', 'ы', 'и', 'й', 'ого', 'его', 'ому', 'ему']
    for suffix in suffixes:
        if word.endswith(suffix) and len(word) > len(suffix) + 1:
            return word[:-len(suffix)]
    return word

def preprocess_text(text):
    words = re.findall(r'\w+', text.lower())
    # Удаляем стоп-слова, короткие слова и применяем стемминг
    return [simple_stem(word) for word in words if word not in stop_words and len(word) > 2]

def extract_keywords(keywords):
    all_words = []
    for keyword in keywords:
        all_words.extend(preprocess_text(keyword))
    
   
    word_freq = defaultdict(int)
    for word in all_words:
        word_freq[word] += 1
    

    return [word for word, freq in word_freq.items() if freq > 1]

def cluster_keywords(keywords):
    extracted_keywords = extract_keywords(keywords)
    clusters = defaultdict(list)

    for keyword in keywords:
        preprocessed = preprocess_text(keyword)
        for extracted_keyword in extracted_keywords:
            if extracted_keyword in preprocessed:
                clusters[extracted_keyword].append(keyword)
    
    clusters = {k: v for k, v in clusters.items() if len(v) >= 3}
    
    return dict(clusters)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        keywords = [kw.strip() for kw in request.form['keywords'].split('\n') if kw.strip()]
        region = request.form['region']
        
        clusters = cluster_keywords(keywords)
        
        return render_template('results.html', clusters=clusters, region=region)
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)