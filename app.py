from flask import Flask, render_template, request, flash, redirect, url_for
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
import re  # Impor modul 're' untuk validasi regex email

app = Flask(__name__)

# --- Konfigurasi MySQL ---
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'  # Ganti dengan username Anda
app.config['MYSQL_PASSWORD'] = ''  # Ganti dengan password Anda
app.config['MYSQL_DB'] = 'db_swipeer'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor' # Ini akan mengembalikan hasil sebagai dictionary

# Kunci rahasia untuk flash messages
app.config['SECRET_KEY'] = 'kunci_rahasia_anda_yang_sangat_aman'

# Inisialisasi MySQL
mysql = MySQL(app)

# --- Fungsi Helper untuk Validasi Email ---
def is_valid_email(email):
    """Fungsi untuk memvalidasi format email menggunakan regex."""
    # Ini adalah implementasi dari valid_email(email) yang ada di gambar Anda
    regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(regex, email) is not None

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        form_type = request.form.get('form_type')

        # --- Logika Registrasi ---
        if form_type == 'register':
            name = request.form.get('name')
            email = request.form.get('email')
            password = request.form.get('password')
            confirm_password = request.form.get('confirm_password')
            gender_form = request.form.get('gender') # "pria" atau "wanita"
            terms = request.form.get('terms') # 'on' jika dicentang, None jika tidak

            # --- VALIDASI TAMBAHAN (Seperti di Gambar) ---
            if not name or not email or not password or not confirm_password or not gender_form:
                flash('Semua field wajib diisi', 'error')
                return redirect(url_for('index'))
            
            if not terms:
                flash('Anda harus menyetujui syarat dan ketentuan.', 'error')
                return redirect(url_for('index'))
            
            if not is_valid_email(email):
                flash('Format email tidak valid', 'error')
                return redirect(url_for('index'))
            
            if password != confirm_password:
                flash('Password dan Konfirmasi Password tidak cocok!', 'error')
                return redirect(url_for('index'))
            # --- AKHIR VALIDASI ---

            gender_db = 'male' if gender_form == 'pria' else 'female'
            hashed_password = generate_password_hash(password)

            try:
                cur = mysql.connection.cursor()
                cur.execute("SELECT * FROM users WHERE username = %s OR email = %s", (name, email))
                existing_user = cur.fetchone()

                if existing_user:
                    flash('Username atau Email sudah terdaftar!', 'error')
                    cur.close()
                    return redirect(url_for('index'))

                cur.execute(
                    "INSERT INTO users (username, email, password_hash, gender) VALUES (%s, %s, %s, %s)",
                    (name, email, hashed_password, gender_db)
                )
                mysql.connection.commit()
                cur.close()

                flash(f'Registrasi berhasil untuk {name}!', 'success')
                return redirect(url_for('index'))

            except Exception as e:
                flash(f'Terjadi kesalahan: {e}', 'error')
                return redirect(url_for('index'))

        # --- Logika Login ---
        elif form_type == 'login':
            email = request.form.get('email')
            password = request.form.get('password')

            # --- IMPLEMENTASI LOGIKA DARI GAMBAR ---
            
            # 1. if email == "" or password == "":
            if not email or not password:
                flash('Email dan Password wajib diisi', 'error')
                return redirect(url_for('index'))
            
            # 2. elif not valid_email(email):
            if not is_valid_email(email):
                flash('Format email tidak valid', 'error')
                return redirect(url_for('index'))

            # 3. elif check_user_in_db(email, password):
            try:
                cur = mysql.connection.cursor()
                cur.execute("SELECT * FROM users WHERE email = %s", [email])
                user = cur.fetchone()
                cur.close()

                if user and check_password_hash(user['password_hash'], password):
                    # "Login berhasil"
                    flash(f'Login berhasil! Selamat datang kembali, {user["username"]}!', 'success')
                    # Di sini Anda akan me-redirect ke halaman dashboard
                    return redirect(url_for('index')) 
                else:
                    # 4. else: "Email atau password salah"
                    flash('Email atau password salah', 'error')
                    return redirect(url_for('index'))

            except Exception as e:
                flash(f'Terjadi kesalahan: {e}', 'error')
                return redirect(url_for('index'))
            
            # --- AKHIR IMPLEMENTASI LOGIKA DARI GAMBAR ---

    # Jika metodenya GET, tampilkan halaman
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)