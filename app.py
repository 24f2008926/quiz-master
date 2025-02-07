from app import create_app
from flask import render_template,flash
app = create_app()
app.config['SECRET_KEY']='277372782h282892302hb'
@app.route('/')
def hello():
    return render_template('homepage.html')




if __name__ == '__main__':
    app.run(debug=True)

