from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///laundry.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class LaundryAppointment(db.Model): # Randevu sistemini tanımlar.
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone_number = db.Column(db.String(15), nullable=False)
    machine_no = db.Column(db.Integer, nullable=False)
    appointment_time = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
        return '<LaundryAppointment %r>' % self.id

@app.route('/appointments', methods=['GET']) #Randevuları listeler.
def appointments():
    appointments_ = LaundryAppointment.query.all()
    return jsonify({
        'appointments': [
            {
                'id': appointment.id,
                'name': appointment.name,
                'phone_number': appointment.phone_number,
                'machine_no': appointment.machine_no,
                'appointment_time': appointment.appointment_time.isoformat(),
            } for appointment in appointments_]})

@app.route('/appointments', methods=['POST']) #Yeni bir randevu ekler.
def add_data():
    data = request.get_json()
    try: # Bu kısım formatı düzenler.
        appointment_time = datetime.fromisoformat(data['appointment_time'])
    except ValueError:
        return jsonify({"Message": "Invalid date format! Use ISO 8601 format, e.g., 'YYYY-MM-DDTHH:MM:SS'."})

    new_appointment = LaundryAppointment(
        name=data['name'],
        machine_no=data['machine_no'],
        phone_number=data['phone_number'],
        appointment_time=appointment_time)
    db.session.add(new_appointment)
    db.session.commit()
    return jsonify({"Message": "Appointment added, you have to do laundry within two hours after your appointment time starts!" }), 201

@app.route('/appointments/<int:appointment_id>', methods=['DELETE']) # Randevu siler.
def delete_data(appointment_id):
    appointment = LaundryAppointment.query.get(appointment_id)
    if appointment:
        db.session.delete(appointment)
        db.session.commit()
        return jsonify({"Message": "Appointment deleted!"})
    else:
        return jsonify({"Message": "Appointment not found!"})

@app.route('/appointments/<int:appointment_id>', methods=['PUT']) # Randevu günceller.
def update_data(appointment_id):
    data = request.get_json()
    appointment = LaundryAppointment.query.get(appointment_id)

    if not appointment:
        return jsonify({"Message": "Appointment not found!"})

    appointment.name = data.get('name', appointment.name)
    appointment.phone_number = data.get('phone_number', appointment.phone_number)
    appointment.machine_no = data.get('machine_no', appointment.machine_no)
    appointment.appointment_time = data.get('appointment_time', appointment.starting_time)
    db.session.commit()
    return jsonify({"Message": "Appointment updated!"})

@app.route('/') # index.html'i döndürür.
def index():
    return render_template('index.html')

if __name__ == '__main__': # Veritabanı tablolarını oluşturup programı çalıştırır.
    app.run(debug=True)
    with app.app_context():
        db.create_all()