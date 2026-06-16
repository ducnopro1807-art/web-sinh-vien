import sqlite3
import os

# Xóa file cơ sở dữ liệu cũ nếu đang tồn tại để làm mới hoàn toàn
if os.path.exists('database.db'):
    os.remove('database.db')

conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# 1. Tạo bảng sinhvien (lưu hồ sơ và ảnh đại diện)
cursor.execute('''
    CREATE TABLE IF NOT EXISTS sinhvien (
        username TEXT PRIMARY KEY,
        password TEXT,
        hoten TEXT,
        lop TEXT,
        avatar TEXT
    )
''')

# 2. Tạo bảng diem_so (Điểm QT và CK)
cursor.execute('''
    CREATE TABLE IF NOT EXISTS diem_so (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        ten_mon TEXT,
        tin_chi INTEGER,
        diem_qt REAL,
        diem_ck REAL,
        FOREIGN KEY(username) REFERENCES sinhvien(username)
    )
''')

# 3. Tạo bảng thoi_khoa_bieu (Lịch học)
cursor.execute('''
    CREATE TABLE IF NOT EXISTS thoi_khoa_bieu (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        noi_dung TEXT,
        FOREIGN KEY(username) REFERENCES sinhvien(username)
    )
''')

# 4. Thêm tài khoản mẫu ban đầu
cursor.execute('''
    INSERT INTO sinhvien (username, password, hoten, lop, avatar)
    VALUES ('sinhvien1', '123456', 'Nguyễn Văn A', 'K65-CNTT', 'https://cdn-icons-png.flaticon.com/512/3135/3135715.png')
''')

# Thêm các môn học mẫu
cac_mon_mau = [
    ('sinhvien1', 'Toán Cao Cấp', 3, 8.0, 9.0),
    ('sinhvien1', 'Vật Lý Đại Cương', 3, 6.5, 7.5),
    ('sinhvien1', 'Hóa Học Đại Cương', 2, 4.0, 4.5) # Môn này tính ra sẽ Bị Trượt để test tính năng
]
cursor.executemany('INSERT INTO diem_so (username, ten_mon, tin_chi, diem_qt, diem_ck) VALUES (?, ?, ?, ?, ?)', cac_mon_mau)

# Thêm lịch học mẫu
lich_mau = [
    ('sinhvien1', 'Thứ 2: Sáng Toán Cao Cấp (Phòng 301)'),
    ('sinhvien1', 'Thứ 4: Chiều Vật Lý Đại Cương (Phòng 102)'),
    ('sinhvien1', 'Thứ 6: Sáng Lập Trình Cơ Bản (Phòng Máy 5)')
]
cursor.executemany('INSERT INTO thoi_khoa_bieu (username, noi_dung) VALUES (?, ?)', lich_mau)

conn.commit()
conn.close()
print("Đã khởi tạo Cơ sở dữ liệu mới thành công!")