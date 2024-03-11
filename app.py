from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import os
import json
from datetime import datetime

app = Flask(__name__)
app.secret_key = '这是一个非常安全的秘密密钥'

def ensure_file_exists(file_path):
    if not os.path.exists(file_path):
        with open(file_path, 'w') as f:
            if 'json' in file_path:
                json.dump([], f)

def load_posts():
    ensure_file_exists('posts.json')
    with open('posts.json', 'r') as f:
        return json.load(f)

def save_posts(posts):
    with open('posts.json', 'w') as f:
        json.dump(posts, f, ensure_ascii=False, indent=4)

def load_users():
    ensure_file_exists('users.json')
    with open('users.json', 'r') as f:
        return json.load(f)

def save_users(users):
    with open('users.json', 'w') as f:
        json.dump(users, f, ensure_ascii=False, indent=4)

@app.route('/')
def home():
    if 'username' not in session:
        return redirect(url_for('login'))
    posts = load_posts()
    return render_template('index.html', posts=posts)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        users = load_users()
        user = next((user for user in users if user['username'] == username), None)
        if user and check_password_hash(user['password'], password):
            session['username'] = username
            flash('登录成功！')
            return redirect(url_for('home'))
        flash('登录失败。请检查您的用户名和密码。')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('您已成功登出。')
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        users = load_users()
        if any(user['username'] == username for user in users):
            flash('用户名已存在。')
            return redirect(url_for('register'))
        users.append({'username': username, 'password': generate_password_hash(password)})
        save_users(users)
        flash('注册成功！现在您可以登录了。')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/publish', methods=['GET', 'POST'])
def publish():
    if 'username' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        # 从表单中获取标题和内容
        title = request.form['title']
        content = request.form['content']
        # 载入现有的文章列表
        posts = load_posts()
        # 将新文章添加到列表中，包括标题、内容和时间戳
        posts.append({
            'title': title,
            'content': content,
            'author': session['username'],
            'timestamp': datetime.utcnow().isoformat()  # 添加 UTC 时间戳
        })
        # 将更新后的文章列表保存回文件
        save_posts(posts)
        # 通知用户文章发布成功
        flash('文章发布成功！')
        return redirect(url_for('home'))
    return render_template('publish.html')

@app.route('/posts')
def posts():
    if 'username' not in session:
        return redirect(url_for('login'))
    posts = load_posts()
    return render_template('posts.html', posts=posts)

if __name__ == '__main__':
    app.run(debug=True)
