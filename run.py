from app.main import app

if __name__ == '__main__':
    app.secret_key = os.urandom(24)
    app.run(debug=True)
