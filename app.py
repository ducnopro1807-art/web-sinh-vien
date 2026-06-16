import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = 'nute_secret_key_secret'

# Cấu hình thư mục lưu ảnh đại diện sinh viên tải lên
UPLOAD_FOLDER = os.path.join('static', 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

DATABASE = 'database.db'

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# TỰ ĐỘNG KHỞI TẠO DATABASE VÀ DỮ LIỆU MẪU BAN ĐẦU
def init_db():
    conn = get_db()
    # 1. Tạo bảng sinhvien
    conn.execute('''
        CREATE TABLE IF NOT EXISTS sinhvien (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            hoten TEXT NOT NULL,
            lop TEXT NOT NULL,
            avatar TEXT NOT NULL
        )
    ''')
    # 2. Tạo bảng điểm số
    conn.execute('''
        CREATE TABLE IF NOT EXISTS diem (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            ten_mon TEXT NOT NULL,
            tin_chi INTEGER NOT NULL,
            diem_qt REAL NOT NULL,
            diem_ck REAL NOT NULL,
            diem_tb REAL NOT NULL,
            trang_thai TEXT NOT NULL
        )
    ''')
    # 3. Tạo bảng thời khóa biểu
    conn.execute('''
        CREATE TABLE IF NOT EXISTS lich (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            noi_dung TEXT NOT NULL
        )
    ''')
    
    # TỰ ĐỘNG CHÈN TÀI KHOẢN MẪU CỦA BẠN NẾU CHƯA CÓ
    user = conn.execute('SELECT * FROM sinhvien WHERE username = ?', ('VUMINHDUC',)).fetchone()
    if not user:
        conn.execute('''
            INSERT INTO sinhvien (username, password, hoten, lop, avatar)
            VALUES (?, ?, ?, ?, ?)
        ''', ('VUMINHDUC', '123456', 'Vũ Minh Đức', 'K19-DHOTO19A', 'https://cdn-icons-png.flaticon.com/512/3135/3135715.png'))
        
        # Chèn sẵn vài môn học mẫu cho sinh động
        conn.execute('INSERT INTO diem (username, ten_mon, tin_chi, diem_qt, diem_ck, diem_tb, trang_thai) VALUES (?,?,?,?,?,?,?)',
                     ('VUMINHDUC', 'Công nghệ Chẩn đoán Ô tô', 3, 8.5, 8.0, 8.2, 'Đạt'))
        conn.execute('INSERT INTO diem (username, ten_mon, tin_chi, diem_qt, diem_ck, diem_tb, trang_thai) VALUES (?,?,?,?,?,?,?)',
                     ('VUMINHDUC', 'Lập trình Python cơ bản', 3, 9.0, 7.5, 8.1, 'Đạt'))
                     
        # Chèn sẵn lịch học mẫu
        conn.execute('INSERT INTO lich (username, noi_dung) VALUES (?, ?)', 
                     ('VUMINHDUC', 'Thứ 2 (Tiết 1-4): Thực hành Điện ô tô - Xưởng trường'))
        conn.execute('INSERT INTO lich (username, noi_dung) VALUES (?, ?)', 
                     ('VUMINHDUC', 'Thứ 5 (Tiết 5-7): Lý thuyết Động cơ đốt trong - P.402'))
        
    conn.commit()
    conn.close()

# Chạy khởi tạo DB ngay khi khởi động app
init_db()

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password'].strip()
        
        conn = get_db()
        user = conn.execute('SELECT * FROM sinhvien WHERE username = ? AND password = ?', (username, password)).fetchone()
        conn.close()
        
        if user:
            session['username'] = user['username']
            return redirect(url_for('dashboard'))
        else:
            return "Sai tài khoản hoặc mật khẩu! Hãy thử lại với: VUMINHDUC mật khẩu 123456"
            
    return '''
        <div style="max-width:300px; margin:100px auto; padding:20px; border:1px solid #ccc; font-family:sans-serif; border-radius:8px;">
            <h3 style="text-align:center;">ĐĂNG NHẬP HỆ THỐNG NUTE</h3>
            <form method="POST">
                Tên đăng nhập: <input type="text" name="username" style="width:100%; padding:8px; margin:8px 0;" value="VUMINHDUC" required><br>
                Mật khẩu: <input type="password" name="password" style="width:100%; padding:8px; margin:8px 0;" value="123456" required><br>
                <button type="submit" style="width:100%; padding:10px; background:#2c3e50; color:white; border:none; border-radius:4px; cursor:pointer;">Đăng nhập</button>
            </form>
        </div>
    '''

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))
        
    conn = get_db()
    # Lấy thông tin cá nhân sinh viên
    user_info = conn.execute('SELECT * FROM sinhvien WHERE username = ?', (session['username'],)).fetchone()
    # Lấy điểm số
    diem_so = conn.execute('SELECT * FROM diem WHERE username = ?', (session['username'],)).fetchall()
    # Lấy lịch học
    lich_hoc = conn.execute('SELECT * FROM lich WHERE username = ?', (session['username'],)).fetchall()
    conn.close()
    
    return render_template('dashboard.html', sv=user_info, diem_so=diem_so, lich_hoc=lich_hoc)

@app.route('/update_profile', methods=['POST'])
def update_profile():
    if 'username' not in session:
        return redirect(url_for('login'))
        
    hoten = request.form['hoten']
    lop = request.form['lop']
    new_username = request.form['username']
    password = request.form['password']
    
    conn = get_db()
    user_info = conn.execute('SELECT * FROM sinhvien WHERE username = ?', (session['username'],)).fetchone()
    avatar_path = user_info['avatar']
    
    # Xử lý file ảnh nếu sinh viên upload ảnh mới
    file = request.files.get('avatar_file')
    if file and file.filename != '':
        filename = f"avatar_{new_username}_{file.filename}"
        full_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(full_path)
        avatar_path = '/' + full_path.replace('\\', '/')

    # Cập nhật thông tin vào DB
    conn.execute('''
        UPDATE sinhvien 
        SET username = ?, password = ?, hoten = ?, lop = ?, avatar = ?
        WHERE username = ?
    ''', (new_username, password, hoten, lop, avatar_path, session['username']))
    
    # Nếu đổi username, cập nhật luôn cả bảng điểm và bảng lịch
    if new_username != session['username']:
        conn.execute('UPDATE diem SET username = ? WHERE username = ?', (new_username, session['username']))
        conn.execute('UPDATE lich SET username = ? WHERE username = ?', (new_username, session['username']))
        session['username'] = new_username
        
    conn.commit()
    conn.close()
    return redirect(url_for('dashboard'))

@app.route('/add_grade', methods=['POST'])
def add_grade():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    ten_mon = request.form['new_mon']
    tin_chi = int(request.form['new_tc'])
    diem_qt = float(request.form['new_diem_qt'])
    diem_ck = float(request.form['new_diem_ck'])
    
    diem_tb = round((diem_qt * 0.4) + (diem_ck * 0.6), 2)
    trang_thai = "Đạt" if diem_tb >= 4.0 else "Học lại"
    
    conn = get_db()
    conn.execute('''
        INSERT INTO diem (username, ten_mon, tin_chi, diem_qt, diem_ck, diem_tb, trang_thai)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (session['username'], ten_mon, tin_chi, diem_qt, diem_ck, diem_tb, trang_thai))
    conn.commit()
    conn.close()
    return redirect(url_for('dashboard'))

@app.route('/edit_grade', methods=['POST'])
def edit_grade():
    if 'username' not in session:
        return redirect(url_for('login'))
        
    mon_id = request.form['mon_id']
    diem_qt = float(request.form['diem_qt'])
    diem_ck = float(request.form['diem_ck'])
    
    diem_tb = round((diem_qt * 0.4) + (diem_ck * 0.6), 2)
    trang_thai = "Đạt" if diem_tb >= 4.0 else "Học lại"
    
    conn = get_db()
    conn.execute('''
        UPDATE diem SET diem_qt = ?, diem_ck = ?, diem_tb = ?, trang_thai = ?
        WHERE id = ? AND username = ?
    ''', (diem_qt, diem_ck, diem_tb, trang_thai, mon_id, session['username']))
    conn.commit()
    conn.close()
    return redirect(url_for('dashboard'))

@app.route('/delete_grade/<int:id>')
def delete_grade(id):
    if 'username' not in session:
        return redirect(url_for('login'))
    conn = get_db()
    conn.execute('DELETE FROM diem WHERE id = ? AND username = ?', (id, session['username']))
    conn.commit()
    conn.close()
    return redirect(url_for('dashboard'))

@app.route('/add_schedule', methods=['POST'])
def add_schedule():
    if 'username' not in session:
        return redirect(url_for('login'))
    noi_dung = request.form['new_lich']
    conn = get_db()
    conn.execute('INSERT INTO lich (username, noi_dung) VALUES (?, ?)', (session['username'], noi_dung))
    conn.commit()
    conn.close()
    return redirect(url_for('dashboard'))

@app.route('/delete_schedule/<int:id>')
def delete_schedule(id):
    if 'username' not in session:
        return redirect(url_for('login'))
    conn = get_db()
    conn.execute('DELETE FROM lich WHERE id = ? AND username = ?', (id, session['username']))
    conn.commit()
    conn.close()
    return redirect(url_for('dashboard'))

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)