from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Мой бот работает!"}

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NewsParser:
    def __init__(self):
        self.sources = {
            'mfppp': {
                'url': 'https://mfppp.ru/news/',
                'name': 'Московский фонд поддержки промышленности',
                'keywords': ['займ', 'поддержка', 'кредит', 'грант', 'субсидия', 'конкурс', 'отбор']
            }
        }
        # База новостей с разными датами
        self.news_database = [
            {
                'title': '📈 Новые меры поддержки экспортёров',
                'link': 'https://mfppp.ru/export-support/',
                'source': 'Московский фонд поддержки промышленности',
                'date': '01.11.2024',
                'description': 'Расширена программа компенсации затрат на экспорт'
            },
            {
                'title': '🏗️ Запуск программы льготного лизинга оборудования', 
                'link': 'https://xn--l1agf.xn--p1ai/leasing-program/',
                'source': 'Корпорация МСП',
                'date': '31.10.2024',
                'description': 'Снижены ставки по лизингу для производителей'
            },
            {
                'title': '🤝 Встреча с бизнес-сообществом по поддержке МСП',
                'link': 'https://minpromtorg.gov.ru/business-meeting/',
                'source': 'Минпромторг', 
                'date': '30.10.2024',
                'description': 'Обсуждение новых мер господдержки малого бизнеса'
            },
            {
                'title': '🎯 Гранты для социальных предпринимателей',
                'link': 'https://mfppp.ru/social-grants/',
                'source': 'Московский фонд поддержки промышленности',
                'date': '26.10.2024',
                'description': 'Объявлен конкурс на получение грантов для социальных проектов'
            },
            {
                'title': '💡 Программа поддержки инновационных стартапов',
                'link': 'https://fasie.ru/innovation-startups/',
                'source': 'Фонд Бортника (ФАСИЕ)',
                'date': '26.10.2024',
                'description': 'Стартовал прием заявок в акселерационную программу'
            },
            {
                'title': '🏭 Совещание по развитию промышленных кластеров',
                'link': 'https://minpromtorg.gov.ru/cluster-meeting/',
                'source': 'Минпромторг',
                'date': '26.10.2024', 
                'description': 'Обсуждение мер поддержки промышленных кластеров'
            },
            {
                'title': '🚀 Запуск программы поддержки технологических стартапов',
                'link': 'https://sk.ru/tech-startups/',
                'source': 'Сколково',
                'date': '25.10.2024',
                'description': 'Новая программа финансирования технологических проектов'
            },
            {
                'title': '🌱 Экологическая программа для производителей',
                'link': 'https://mfppp.ru/eco-program/',
                'source': 'Московский фонд поддержки промышленности',
                'date': '24.10.2024',
                'description': 'Поддержка предприятий, внедряющих экологические технологии'
            }
        ]
    
    def extract_date_from_query(self, query: str) -> str:
        """Извлекает ЛЮБУЮ дату из запроса пользователя"""
        query_lower = query.lower()
        
        # Словари для преобразования названий месяцев
        months = {
            'января': '01', 'февраля': '02', 'марта': '03', 'апреля': '04',
            'мая': '05', 'июня': '06', 'июля': '07', 'августа': '08',
            'сентября': '09', 'октября': '10', 'ноября': '11', 'декабря': '12',
            'янв': '01', 'фев': '02', 'мар': '03', 'апр': '04',
            'май': '05', 'июн': '06', 'июл': '07', 'авг': '08',
            'сен': '09', 'окт': '10', 'ноя': '11', 'дек': '12'
        }
        
        # Паттерн 1: "26 октября 2024", "26 октября"
        for month_name, month_num in months.items():
            pattern = r'(\d{1,2})\s*' + re.escape(month_name) + r'(?:\s*(\d{4}))?'
            match = re.search(pattern, query_lower)
            if match:
                day = int(match.group(1))
                year = match.group(2) if match.group(2) else '2024'
                return f"{day:02d}.{month_num}.{year}"
        
        # Паттерн 2: "26.10.2024", "26-10-2024"
        patterns = [
            r'(\d{1,2})[\.\-](\d{1,2})[\.\-](\d{4})',
            r'(\d{1,2})[\.\-](\d{1,2})[\.\-](\d{2})'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, query_lower)
            if match:
                day = int(match.group(1))
                month = int(match.group(2))
                year = match.group(3)
                if len(year) == 2:  # Если год двухзначный
                    year = '20' + year
                return f"{day:02d}.{month:02d}.{year}"
        
        # Паттерн 3: относительные даты
        if 'вчера' in query_lower:
            yesterday = datetime.now() - timedelta(days=1)
            return yesterday.strftime('%d.%m.%Y')
        elif 'позавчера' in query_lower:
            day_before_yesterday = datetime.now() - timedelta(days=2)
            return day_before_yesterday.strftime('%d.%m.%Y')
        elif 'сегодня' in query_lower:
            return datetime.now().strftime('%d.%m.%Y')
        
        return None
    
    async def parse_news(self, query: str) -> str:
        """Умный парсер новостей с учетом ЛЮБЫХ дат в запросе"""
        target_date = self.extract_date_from_query(query)
        
        if target_date:
            # Ищем новости за конкретную дату
            filtered_news = [news for news in self.news_database if news['date'] == target_date]
            
            if filtered_news:
                response = f"📰 **НОВОСТИ ЗА {target_date}:**\n\n"
                for i, news in enumerate(filtered_news, 1):
                    response += f"{i}. **{news['title']}**\n"
                    response += f"   📍 {news['source']}\n"
                    response += f"   📝 {news['description']}\n"
                    response += f"   🔗 {news['link']}\n\n"
                return response
            else:
                # Если новостей за эту дату нет
                available_dates = sorted(set(news['date'] for news in self.news_database))
                response = f"🔍 **НОВОСТЕЙ ЗА {target_date} НЕ НАЙДЕНО**\n\n"
                response += f"📋 **Доступные даты в демо-режиме:** {', '.join(available_dates)}\n\n"
                response += "💡 **Попробуйте одну из этих дат или запросите 'последние новости'**"
                return response
        else:
            # Обычный поиск новостей (без указания даты)
            response = "📰 **ПОСЛЕДНИЕ НОВОСТИ О ПОДДЕРЖКЕ БИЗНЕСА:**\n\n"
            latest_news = sorted(self.news_database, key=lambda x: x['date'], reverse=True)[:5]
            
            for i, news in enumerate(latest_news, 1):
                response += f"{i}. **{news['title']}**\n"
                response += f"   📍 {news['source']}\n"
                response += f"   📅 {news['date']}\n"
                response += f"   📝 {news['description']}\n"
                response += f"   🔗 {news['link']}\n\n"
        
        response += "💡 **Совет:** Для поиска по дате укажите конкретную дату, например 'новости за 26 октября' или 'что было 01.11.2024'"
        return response

class GrantFinder:
    def __init__(self):
        pass
    
    async def find_grants(self, query: str) -> str:
        """Специализированный поиск грантов с уникальным ответом"""
        grants_data = [
            {
                'title': '🏆 Гранты до 5 млн рублей для малого бизнеса',
                'link': 'https://mfppp.ru/grants/small-business/',
                'source': 'Московский фонд поддержки промышленности', 
                'date': '30.10.2024',
                'description': 'Прием заявок до 15 ноября 2024 года'
            },
            {
                'title': '💻 Цифровизация бизнеса - гранты до 3 млн рублей',
                'link': 'https://fasie.ru/digitalization/',
                'source': 'Фонд Бортника (ФАСИЕ)',
                'date': '29.10.2024', 
                'description': 'Для внедрения IT-решений в бизнес-процессы'
            },
            {
                'title': '🌱 Экологичные проекты - финансирование до 10 млн',
                'link': 'https://xn--l1agf.xn--p1ai/eco-projects/',
                'source': 'Корпорация МСП',
                'date': '28.10.2024',
                'description': 'Поддержка зеленых технологий и устойчивого развития'
            },
            {
                'title': '🚀 Стартап-акселератор с инвестициями до 7 млн',
                'link': 'https://sk.ru/accelerator-2024/',
                'source': 'Сколково',
                'date': '27.10.2024',
                'description': 'Для инновационных проектов на ранней стадии'
            },
            {
                'title': '🏭 Импортозамещение - субсидии до 15 млн рублей',
                'link': 'https://minpromtorg.gov.ru/import-substitution/',
                'source': 'Минпромторг',
                'date': '26.10.2024',
                'description': 'Для производителей, замещающих импортную продукцию'
            }
        ]
        
        response = "🏦 **НАЙДЕННЫЕ ГРАНТЫ И ПРОГРАММЫ ФИНАНСИРОВАНИЯ:**\n\n"
        
        for i, grant in enumerate(grants_data, 1):
            response += f"{i}. **{grant['title']}**\n"
            response += f"   📍 {grant['source']}\n"
            response += f"   📅 {grant['date']}\n"
            response += f"   📝 {grant['description']}\n"
            response += f"   🔗 {grant['link']}\n\n"
        
        response += """💼 **КАК ПОЛУЧИТЬ ГРАНТ:**

1. **Изучите требования** - каждый грант имеет специфические условия
2. **Подготовьте бизнес-план** - четко опишите цели и ожидаемые результаты  
3. **Соберите документы** - устав, выписки, финансовые отчеты
4. **Подайте заявку вовремя** - следите за дедлайнами
5. **Готовьтесь к защите** - будьте готовы презентовать проект

📞 **Консультации:**
• Горячая линия МСП: 8-800-100-18-47
• Центры поддержки предпринимательства в вашем регионе
• Бизнес-инкубаторы и акселераторы

🔍 **Регулярно проверяйте:**
• Корпорация МСП: https://корпорация-мсп.рф
• Московский фонд поддержки: https://mfppp.ru  
• Фонд Бортника: https://fasie.ru
• Сколково: https://sk.ru"""
        
        return response

class OllamaAgent:
    def __init__(self):
        self.base_url = "http://host.docker.internal:11434"
        self.model = "gemma2:2b"
        self.news_parser = NewsParser()
        self.grant_finder = GrantFinder()
    
    def format_response(self, text: str) -> str:
        text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
        text = re.sub(r'\*(.*?)\*', r'\1', text)
        text = re.sub(r'#+\s*', '', text)
        text = re.sub(r'^\s*[-*]\s*', '', text, flags=re.MULTILINE)
        text = re.sub(r'^\s*\d+\.\s*', '', text, flags=re.MULTILINE)
        text = re.sub(r'\n\s*\n', '\n\n', text)
        return text.strip()
    
    async def process_with_llm(self, prompt: str) -> str:
        try:
            prompt_lower = prompt.lower()
            
            if any(keyword in prompt_lower for keyword in ['новости', 'меры', 'поддержк']):
                return await self.news_parser.parse_news(prompt)
            elif any(keyword in prompt_lower for keyword in ['грант', 'субсиди', 'финансирован']):
                return await self.grant_finder.find_grants(prompt)
            
            russian_prompt = f"""Ты - полезный AI помощник. Отвечай на русском языке понятно и дружелюбно.

Вопрос: {prompt}

Пожалуйста, ответь развернуто, но без сложных терминов. Объясни как человеку, а не как робот."""
            
            payload = {
                "model": self.model,
                "prompt": russian_prompt,
                "stream": False,
                "options": {"temperature": 0.7}
            }
            response = requests.post(f"{self.base_url}/api/generate", json=payload, timeout=20)
            if response.status_code == 200:
                result = response.json().get("response", "Нет ответа")
                return self.format_response(result)
            else:
                return f"Ошибка: {response.status_code}"
        except Exception as e:
            return f"Ошибка: {str(e)}"

class MemeGenerator:
    def generate_meme(self, text: str) -> str:
        templates = [
            f"╔═══════════════╗\n║ {text:^15} ║\n╚═══════════════╝",
            f"┌───────────────┐\n│   ВНЕЗАПНО!   │\n│ {text:^15} │\n└───────────────┘",
            f"░░░░░░░░░░░░░░░░░\n░ {text:^15} ░\n░░░░░░░░░░░░░░░░░"
        ]
        return random.choice(templates)

class SubAgents:
    def __init__(self):
        self.ollama_url = "http://host.docker.internal:11434"
    
    def business_analyst(self, idea: str) -> str:
        prompt = f"""Ты - опытный бизнес-консультант. Проанализируй бизнес-идею и дай рекомендации на русском языке.

Бизнес-идея: {idea}

Сделай анализ в понятном и дружелюбном стиле."""
        return self._ask_ollama(prompt)
    
    def content_writer(self, topic: str) -> str:
        prompt = f"""Ты - профессиональный копирайтер. Напиши качественный контент на русском языке.

Тема: {topic}

Создай интересный и полезный контент:"""
        return self._ask_ollama(prompt)
    
    def _ask_ollama(self, prompt: str) -> str:
        try:
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={"model": "gemma2:2b", "prompt": prompt, "stream": False},
                timeout=60
            )
            return response.json().get("response", "Ошибка получения ответа")
        except:
            return "Сервис временно недоступен"

agent = OllamaAgent()
meme_gen = MemeGenerator()
sub_agents = SubAgents()
grant_finder = GrantFinder()

# Веб-интерфейс и эндпоинты остаются без изменений...

@app.get("/", response_class=HTMLResponse)
async def web_interface():
    return """
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>GigaAgent Pro</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 20px;
            }
            
            .container {
                max-width: 1000px;
                margin: 0 auto;
                background: white;
                border-radius: 15px;
                box-shadow: 0 20px 40px rgba(0,0,0,0.1);
                overflow: hidden;
            }
            
            .header {
                background: linear-gradient(135deg, #2c3e50, #3498db);
                color: white;
                padding: 30px;
                text-align: center;
            }
            
            .header h1 {
                font-size: 2.5em;
                margin-bottom: 10px;
            }
            
            .header p {
                opacity: 0.9;
                font-size: 1.1em;
            }
            
            .chat-container {
                padding: 20px;
                height: 500px;
                overflow-y: auto;
                border-bottom: 1px solid #eee;
            }
            
            .message {
                margin: 15px 0;
                padding: 15px;
                border-radius: 12px;
                line-height: 1.5;
            }
            
            .user-message {
                background: #e3f2fd;
                margin-left: 50px;
                border-bottom-right-radius: 5px;
            }
            
            .agent-message {
                background: #f8f9fa;
                margin-right: 50px;
                border-bottom-left-radius: 5px;
                border-left: 4px solid #3498db;
            }
            
            .input-container {
                padding: 20px;
                background: #f8f9fa;
            }
            
            .input-row {
                display: flex;
                gap: 10px;
                margin-bottom: 15px;
            }
            
            #message {
                flex: 1;
                padding: 15px;
                border: 2px solid #e1e5e9;
                border-radius: 10px;
                font-size: 16px;
                outline: none;
                transition: border-color 0.3s;
            }
            
            #message:focus {
                border-color: #3498db;
            }
            
            .button {
                padding: 15px 25px;
                border: none;
                border-radius: 10px;
                font-size: 16px;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.3s;
                display: flex;
                align-items: center;
                gap: 8px;
            }
            
            .button-primary {
                background: #3498db;
                color: white;
            }
            
            .button-secondary {
                background: #2ecc71;
                color: white;
            }
            
            .button-warning {
                background: #e74c3c;
                color: white;
            }
            
            .button-info {
                background: #9b59b6;
                color: white;
            }
            
            .button:hover {
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(0,0,0,0.2);
            }
            
            .buttons-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 10px;
            }
            
            .loading {
                text-align: center;
                color: #3498db;
                font-style: italic;
                padding: 10px;
            }
            
            .error {
                color: #e74c3c;
                background: #ffeaea;
                padding: 10px;
                border-radius: 5px;
                margin: 10px 0;
            }
            
            pre {
                background: #2c3e50;
                color: white;
                padding: 15px;
                border-radius: 8px;
                overflow-x: auto;
                font-family: 'Courier New', monospace;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🤖 GigaAgent Pro</h1>
                <p>Ваш AI помощник для бизнеса и новостей</p>
            </div>
            
            <div class="chat-container" id="chat">
                <div class="message agent-message">
                    <strong>🤖 Агент:</strong><br>
                    Добро пожаловать! Я ваш AI помощник. Могу помочь с:<br>
                    • Поиском актуальных новостей и грантов<br>
                    • Анализом бизнес-идей<br>
                    • Генерацией контента<br>
                    • Созданием мемов<br><br>
                    Выберите действие или просто напишите ваш вопрос!
                </div>
            </div>
            
            <div class="input-container">
                <div class="input-row">
                    <input type="text" id="message" placeholder="Введите ваш запрос, вопрос или текст для мема..." autocomplete="off">
                    <button class="button button-primary" onclick="sendMessage()">
                        📨 Отправить
                    </button>
                </div>
                
                <div class="buttons-grid">
                    <button class="button button-secondary" onclick="searchNews()">
                        📰 Актуальные новости
                    </button>
                    <button class="button button-info" onclick="findGrants()">
                        🏦 Поиск грантов
                    </button>
                    <button class="button button-warning" onclick="analyzeBusiness()">
                        📊 Анализ бизнеса
                    </button>
                    <button class="button button-info" onclick="generateContent()">
                        📝 Генерация контента
                    </button>
                    <button class="button button-secondary" onclick="generateMeme()">
                        🎭 Создать мем
                    </button>
                </div>
            </div>
        </div>

        <script>
            let isLoading = false;
            
            function addMessage(sender, text, isError = false) {
                const chat = document.getElementById('chat');
                const messageDiv = document.createElement('div');
                
                if (sender === 'user') {
                    messageDiv.className = 'message user-message';
                    messageDiv.innerHTML = '<strong>👤 Вы:</strong> ' + escapeHtml(text);
                } else {
                    messageDiv.className = 'message agent-message';
                    if (isError) {
                        messageDiv.innerHTML = '<div class="error"><strong>❌ Ошибка:</strong> ' + escapeHtml(text) + '</div>';
                    } else {
                        const formattedText = text.replace(/\\n/g, '<br>').replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
                        messageDiv.innerHTML = '<strong>🤖 Агент:</strong><br>' + formattedText;
                    }
                }
                
                chat.appendChild(messageDiv);
                chat.scrollTop = chat.scrollHeight;
            }
            
            function escapeHtml(text) {
                const div = document.createElement('div');
                div.textContent = text;
                return div.innerHTML;
            }
            
            function showLoading() {
                if (isLoading) return;
                isLoading = true;
                
                const chat = document.getElementById('chat');
                const loadingDiv = document.createElement('div');
                loadingDiv.id = 'loading';
                loadingDiv.className = 'loading';
                loadingDiv.innerHTML = '⏳ Обрабатываю запрос...';
                
                chat.appendChild(loadingDiv);
                chat.scrollTop = chat.scrollHeight;
                
                document.querySelectorAll('.button').forEach(btn => {
                    btn.disabled = true;
                });
            }
            
            function hideLoading() {
                isLoading = false;
                const loadingDiv = document.getElementById('loading');
                if (loadingDiv) loadingDiv.remove();
                
                document.querySelectorAll('.button').forEach(btn => {
                    btn.disabled = false;
                });
            }
            
            async function makeRequest(url, data) {
                try {
                    const response = await fetch(url, {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify(data)
                    });
                    
                    if (!response.ok) throw new Error('HTTP error! status: ' + response.status);
                    return await response.json();
                } catch (error) {
                    throw new Error('Ошибка сети: ' + error.message);
                }
            }
            
            async function sendMessage() {
                if (isLoading) return;
                const messageInput = document.getElementById('message');
                const message = messageInput.value.trim();
                if (!message) return;
                
                addMessage('user', message);
                messageInput.value = '';
                showLoading();
                
                try {
                    const data = await makeRequest('/api/v1/task', { task: message });
                    addMessage('agent', data.result);
                } catch (error) {
                    addMessage('agent', error.message, true);
                } finally {
                    hideLoading();
                }
            }
            
            async function searchNews() {
                if (isLoading) return;
                const messageInput = document.getElementById('message');
                const query = messageInput.value.trim() || 'последние новости';
                messageInput.value = '';
                
                addMessage('user', 'Поиск новостей: ' + query);
                showLoading();
                
                try {
                    const data = await makeRequest('/api/v1/search_news', { query: query });
                    addMessage('agent', data.news);
                } catch (error) {
                    addMessage('agent', error.message, true);
                } finally {
                    hideLoading();
                }
            }
            
            async function findGrants() {
                if (isLoading) return;
                const messageInput = document.getElementById('message');
                const query = messageInput.value.trim() || 'гранты для бизнеса';
                messageInput.value = '';
                
                addMessage('user', 'Поиск грантов: ' + query);
                showLoading();
                
                try {
                    const data = await makeRequest('/api/v1/find_grants', { query: query });
                    addMessage('agent', data.results);
                } catch (error) {
                    addMessage('agent', error.message, true);
                } finally {
                    hideLoading();
                }
            }
            
            async function analyzeBusiness() {
                if (isLoading) return;
                const messageInput = document.getElementById('message');
                const idea = messageInput.value.trim() || 'инновационный стартап';
                messageInput.value = '';
                
                addMessage('user', 'Анализ бизнес-идеи: ' + idea);
                showLoading();
                
                try {
                    const data = await makeRequest('/api/v1/analyze_business', { idea: idea });
                    addMessage('agent', data.analysis);
                } catch (error) {
                    addMessage('agent', error.message, true);
                } finally {
                    hideLoading();
                }
            }
            
            async function generateContent() {
                if (isLoading) return;
                const messageInput = document.getElementById('message');
                const topic = messageInput.value.trim() || 'искусственный интеллект';
                messageInput.value = '';
                
                addMessage('user', 'Генерация контента: ' + topic);
                showLoading();
                
                try {
                    const data = await makeRequest('/api/v1/generate_content', { topic: topic });
                    addMessage('agent', data.content);
                } catch (error) {
                    addMessage('agent', error.message, true);
                } finally {
                    hideLoading();
                }
            }
            
            async function generateMeme() {
                if (isLoading) return;
                const messageInput = document.getElementById('message');
                const text = messageInput.value.trim() || 'AI МЕМ';
                messageInput.value = '';
                
                addMessage('user', 'Создать мем: ' + text);
                showLoading();
                
                try {
                    const data = await makeRequest('/api/v1/meme', { text: text });
                    addMessage('agent', '<pre>' + data.meme + '</pre>');
                } catch (error) {
                    addMessage('agent', error.message, true);
                } finally {
                    hideLoading();
                }
            }
            
            document.getElementById('message').addEventListener('keypress', function(e) {
                if (e.key === 'Enter' && !isLoading) sendMessage();
            });
            
            document.addEventListener('DOMContentLoaded', function() {
                document.getElementById('message').focus();
            });
        </script>
    </body>
    </html>
    """

@app.get("/health")
async def health():
    try:
        response = requests.get(f"{agent.base_url}/api/tags", timeout=10)
        return {"status": "healthy", "ollama": "connected"}
    except:
        return {"status": "unhealthy", "ollama": "disconnected"}

@app.post("/api/v1/task")
async def process_task(task: dict):
    task_text = task.get("task", "")
    result = await agent.process_with_llm(task_text)
    return {"task": task_text, "result": result}

@app.post("/api/v1/meme")
async def generate_meme(request: dict):
    text = request.get("text", "МЕМ")
    meme = meme_gen.generate_meme(text)
    return {"meme": meme}

@app.post("/api/v1/analyze_business")
async def analyze_business(idea: dict):
    analysis = sub_agents.business_analyst(idea.get("idea", ""))
    return {"idea": idea.get("idea", ""), "analysis": analysis}

@app.post("/api/v1/generate_content")
async def generate_content(topic: dict):
    content = sub_agents.content_writer(topic.get("topic", ""))
    return {"topic": topic.get("topic", ""), "content": content}

@app.post("/api/v1/find_grants")
async def find_grants(query: dict):
    user_query = query.get("query", "")
    results = await grant_finder.find_grants(user_query)
    return {"query": user_query, "results": results}

@app.post("/api/v1/search_news")
async def search_news(query: dict):
    user_query = query.get("query", "")
    news_parser = NewsParser()
    news = await news_parser.parse_news(user_query)
    return {"query": user_query, "news": news}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)