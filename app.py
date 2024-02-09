from flask import Flask, render_template, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
import qrcode

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)

class Fruit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    plantation_date = db.Column(db.String(50), nullable=False)
    harvest_date = db.Column(db.String(50), nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    blockchain_hash = db.Column(db.String(256), nullable=False, unique=True)

class FruitForm(FlaskForm):
    name = StringField('Fruit Name')
    plantation_date = StringField('Plantation Date')
    harvest_date = StringField('Harvest Date')
    submit = SubmitField('Add Fruit')

@app.route('/')
def home():
    fruits = Fruit.query.all()
    return render_template('index.html', fruits=fruits)

@app.route('/add_fruit', methods=['GET', 'POST'])
def add_fruit():
    form = FruitForm()
    if form.validate_on_submit():
        name = form.name.data
        plantation_date = form.plantation_date.data
        harvest_date = form.harvest_date.data

        # ทำการสร้าง Block Hash จากข้อมูลของผลไม้
        blockchain_data = f"{name}-{plantation_date}-{harvest_date}"
        blockchain_hash = bcrypt.generate_password_hash(blockchain_data).decode('utf-8')

        # สร้างข้อมูลผลไม้ใน Blockchain
        fruit = Fruit(name=name, plantation_date=plantation_date, harvest_date=harvest_date, owner_id=1, blockchain_hash=blockchain_hash)
        db.session.add(fruit)
        db.session.commit()
        flash('Fruit added successfully!', 'success')
        return redirect(url_for('home'))

    return render_template('add_fruit.html', form=form)

@app.route('/generate_qr/<int:fruit_id>')
def generate_qr(fruit_id):
    fruit = Fruit.query.get_or_404(fruit_id)

    # Generate QR code data
    qr_data = f"Name: {fruit.name}\nPlantation Date: {fruit.plantation_date}\nHarvest Date: {fruit.harvest_date}"

    # Generate QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(qr_data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    # Save QR code image to a file in the static directory
    img_filename = f"qr_codes/fruit_{fruit.id}.png"
    img_path = f"static/{img_filename}"
    img.save(img_path)

    # Render the generate_qr.html template
    return render_template('generate_qr.html', img_filename=img_filename)


# เพิ่มบรรทัดนี้
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
