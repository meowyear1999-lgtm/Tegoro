# Sherlock Telegram Bot - Render.com Deployment Guide

## 🚀 Развертывание на Render.com

### Шаг 1: Зарегистрируйся на Render
1. Открой https://render.com на телефоне
2. Нажми "Sign up"
3. Выбери "Sign up with GitHub"
4. Авторизуйся через GitHub аккаунт

### Шаг 2: Создай новый сервис
1. Нажми "+ New" → выбери "Web Service"
2. Нажми "Connect a repository"
3. Выбери репозиторий **meowyear1999-lgtm/Tegoro**
4. Нажми "Connect"

### Шаг 3: Настройка сервиса
- **Name**: `sherlock-bot` (или любое имя)
- **Environment**: `Python 3`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `python bot.py`
- **Instance Type**: Free (бесплатно!)

### Шаг 4: Установка переменной окружения
1. Прокрути вниз до "Environment"
2. Нажми "Add Environment Variable"
3. Введи:
   - **Key**: `BOT_TOKEN`
   - **Value**: `твой_токен_здесь` (без кавычек!)
4. Нажми "Save"

### Шаг 5: Deploy
1. Нажми "Create Web Service"
2. Жди 2-5 минут, пока деплоится
3. Когда появится зеленая галочка "Live" - готово! ✅

### Проверка работы
- Открой Telegram
- Напиши своему боту `/start`
- Если ответит - всё работает! 🎉

---

## ⚙️ Дополнительные команды

**Просмотр логов:**
- На странице сервиса нажми "Logs"
- Там увидишь все ошибки и события

**Перезапуск:**
- Нажми кнопку "Restart"

**Удаление:**
- Settings → Delete Service

---

## 📝 Важно!

- ⚠️ **Free план на Render**: сервис выключается, если нет трафика 15 минут
- ✅ Решение: напиши боту каждые 14 минут (можно автоматизировать)
- 💰 **Платные планы**: $7/месяц за постоянный сервер

---

## 🔗 Полезные ссылки

- https://render.com (главный сайт)
- https://render.com/docs (документация)
- Помощь: support@render.com

**Готово! Бот работает 24/7!** 🚀
