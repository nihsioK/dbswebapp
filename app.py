
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:admin@35.228.129.140/caregiving'
db = SQLAlchemy(app)

@app.route('/')
def hello_world():
    return 'Hello from Flask!'

class Users(db.Model):
    __tablename__ = 'users'
    user_id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255))
    given_name = db.Column(db.String(255))
    surname = db.Column(db.String(255))
    city = db.Column(db.String(255))
    phone_number = db.Column(db.String(20))
    profile_description = db.Column(db.Text)
    password = db.Column(db.String(255))
    members = db.relationship('Member', backref='user', lazy=True, cascade="all, delete-orphan")
    caregivers = db.relationship('Caregiver', backref='user', lazy=True, cascade="all, delete-orphan")

class Member(db.Model):
    __tablename__ = 'member'
    member_user_id = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='CASCADE'), primary_key=True)
    house_rules = db.Column(db.Text)
    appointment = db.relationship('Appointment', backref='member', lazy=True, cascade="all, delete-orphan")
    addresses = db.relationship('Address', backref='member', lazy=True, cascade="all, delete-orphan")
    job = db.relationship('Job', backref='member', lazy=True, cascade="all, delete-orphan")

class Caregiver(db.Model):
    __tablename__ = 'caregiver'
    caregiver_user_id = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='CASCADE'), primary_key=True)
    photo = db.Column(db.String(255))
    gender = db.Column(db.String(10))
    caregiving_type = db.Column(db.String(255))
    hourly_rate = db.Column(db.Numeric(10, 2))

class Address(db.Model):
    __tablename__ = 'address'
    member_user_id = db.Column(db.Integer, db.ForeignKey('member.member_user_id', ondelete='CASCADE'), primary_key=True)
    house_number = db.Column(db.String(10))
    street = db.Column(db.String(255))
    town = db.Column(db.String(255))

class Appointment(db.Model):
    __tablename__ = 'appointment'
    appointment_id = db.Column(db.Integer, primary_key=True)
    caregiver_user_id = db.Column(db.Integer, db.ForeignKey('caregiver.caregiver_user_id', ondelete='CASCADE'))
    member_user_id = db.Column(db.Integer, db.ForeignKey('member.member_user_id', ondelete='CASCADE'))
    appointment_date = db.Column(db.Date)
    appointment_time = db.Column(db.Time)
    work_hours = db.Column(db.Integer)
    status = db.Column(db.String(255))

class Job(db.Model):
    __tablename__ = 'job'
    job_id = db.Column(db.Integer, primary_key=True)
    member_user_id = db.Column(db.Integer, db.ForeignKey('member.member_user_id', ondelete='CASCADE'))
    required_caregiving_type = db.Column(db.String(255))
    other_requirements = db.Column(db.Text)
    date_posted = db.Column(db.Date)
    job_application = db.relationship('JobApplication', backref='job', lazy=True, cascade="all, delete-orphan")

class JobApplication(db.Model):
    __tablename__ = 'job_application'
    caregiver_user_id = db.Column(db.Integer, db.ForeignKey('caregiver.caregiver_user_id', ondelete='CASCADE'), primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey('job.job_id', ondelete='CASCADE'), primary_key=True)
    date_applied = db.Column(db.Date)


@app.route('/member', methods=['POST'])
def create_member():
    try:
        data = request.get_json()
        new_member = Member(
            member_user_id=data['member_user_id'],
            house_rules=data['house_rules']
        )
        db.session.add(new_member)
        db.session.commit()
        return jsonify({'message': 'Member created successfully'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/members', methods=['GET'])
def get_members():
    members = Member.query.all()
    return jsonify([{'member_user_id': member.member_user_id, 'house_rules': member.house_rules} for member in members])

@app.route('/member/<int:member_user_id>', methods=['GET'])
def get_member(member_user_id):
    member = Member.query.get_or_404(member_user_id)
    return jsonify({'member_user_id': member.member_user_id, 'house_rules': member.house_rules})

@app.route('/member/<int:member_user_id>', methods=['PUT'])
def update_member(member_user_id):
    member = Member.query.get_or_404(member_user_id)
    data = request.get_json()
    member.house_rules = data.get('house_rules', member.house_rules)
    db.session.commit()
    return jsonify({'message': 'Member updated successfully'})

@app.route('/member/<int:member_user_id>', methods=['DELETE'])
def delete_member(member_user_id):
    member = Member.query.get_or_404(member_user_id)
    db.session.delete(member)
    db.session.commit()
    return jsonify({'message': 'Member deleted successfully'})


@app.route('/user', methods=['POST'])
def create_user():
    try:
        data = request.get_json()
        new_user = Users(
            user_id=data['user_id'],
            email=data['email'],
            given_name=data['given_name'],
            surname=data['surname'],
            city=data['city'],
            phone_number=data['phone_number'],
            profile_description=data['profile_description'],
            password=data['password']  # Make sure to hash the password in a real-world application
        )
        db.session.add(new_user)
        db.session.commit()
        return jsonify({'message': 'User created successfully'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/users', methods=['GET'])
def get_users():
    users = Users.query.all()
    return jsonify([{'user_id': user.user_id, 'email': user.email, 'given_name':user.given_name, 'surname':user.surname,'city':user.city, 'phone_number':user.phone_number, 'profile_description':user.profile_description} for user in users])

@app.route('/user/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = Users.query.get_or_404(user_id)
    return jsonify(user.to_dict())

@app.route('/user/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    user = Users.query.get_or_404(user_id)
    data = request.get_json()
    user.email = data.get('email', user.email)
    # Update other fields similarly
    db.session.commit()
    return jsonify({'message': 'User updated successfully'})

@app.route('/user/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    user = Users.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': 'User deleted successfully'})


@app.route('/caregiver', methods=['POST'])
def create_caregiver():
    try:
        data = request.get_json()
        new_caregiver = Caregiver(
            caregiver_user_id=data['caregiver_user_id'],
            photo=data['photo'],
            gender=data['gender'],
            caregiving_type=data['caregiving_type'],
            hourly_rate=data['hourly_rate']
        )
        db.session.add(new_caregiver)
        db.session.commit()
        return jsonify({'message': 'Caregiver created successfully'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/caregivers', methods=['GET'])
def get_caregivers():
    caregivers = Caregiver.query.all()
    return jsonify([caregiver.to_dict() for caregiver in caregivers])

@app.route('/caregiver/<int:caregiver_user_id>', methods=['GET'])
def get_caregiver(caregiver_user_id):
    caregiver = Caregiver.query.get_or_404(caregiver_user_id)
    return jsonify(caregiver.to_dict())

@app.route('/caregiver/<int:caregiver_user_id>', methods=['PUT'])
def update_caregiver(caregiver_user_id):
    caregiver = Caregiver.query.get_or_404(caregiver_user_id)
    data = request.get_json()
    caregiver.photo = data.get('photo', caregiver.photo)
    caregiver.gender = data.get('gender', caregiver.gender)
    caregiver.caregiving_type = data.get('caregiving_type', caregiver.caregiving_type)
    caregiver.hourly_rate = data.get('hourly_rate', caregiver.hourly_rate)
    db.session.commit()
    return jsonify({'message': 'Caregiver updated successfully'})

@app.route('/caregiver/<int:caregiver_user_id>', methods=['DELETE'])
def delete_caregiver(caregiver_user_id):
    caregiver = Caregiver.query.get_or_404(caregiver_user_id)
    db.session.delete(caregiver)
    db.session.commit()
    return jsonify({'message': 'Caregiver deleted successfully'})

@app.route('/address', methods=['POST'])
def create_address():
    try:
        data = request.get_json()
        new_address = Address(
            member_user_id=data['member_user_id'],
            house_number=data['house_number'],
            street=data['street'],
            town=data['town']
        )
        db.session.add(new_address)
        db.session.commit()
        return jsonify({'message': 'Address created successfully'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/addresses', methods=['GET'])
def get_addresses():
    addresses = Address.query.all()
    return jsonify([{'member_user_id': address.member_user_id, 'house_number': address.house_number, 'street': address.street, 'town': address.town} for address in addresses])

@app.route('/address/<int:member_user_id>', methods=['GET'])
def get_address(member_user_id):
    address = Address.query.get_or_404(member_user_id)
    return jsonify({'member_user_id': address.member_user_id, 'house_number': address.house_number, 'street': address.street, 'town': address.town})

@app.route('/address/<int:member_user_id>', methods=['PUT'])
def update_address(member_user_id):
    address = Address.query.get_or_404(member_user_id)
    data = request.get_json()
    address.house_number = data.get('house_number', address.house_number)
    address.street = data.get('street', address.street)
    address.town = data.get('town', address.town)
    db.session.commit()
    return jsonify({'message': 'Address updated successfully'})

@app.route('/address/<int:member_user_id>', methods=['DELETE'])
def delete_address(member_user_id):
    address = Address.query.get_or_404(member_user_id)
    db.session.delete(address)
    db.session.commit()
    return jsonify({'message': 'Address deleted successfully'})


@app.route('/appointment', methods=['POST'])
def create_appointment():
    try:
        data = request.get_json()
        new_appointment = Appointment(
            appointment_id=data['appointment_id'],
            caregiver_user_id=data['caregiver_user_id'],
            member_user_id=data['member_user_id'],
            appointment_date=data['appointment_date'],
            appointment_time=data['appointment_time'],
            work_hours=data['work_hours'],
            status=data['status']
        )
        db.session.add(new_appointment)
        db.session.commit()
        return jsonify({'message': 'Appointment created successfully'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/appointments', methods=['GET'])
def get_appointments():
    appointments = Appointment.query.all()
    return jsonify([appointment.serialize() for appointment in appointments])

@app.route('/appointment/<int:appointment_id>', methods=['GET'])
def get_appointment(appointment_id):
    appointment = Appointment.query.get_or_404(appointment_id)
    return jsonify(appointment.serialize())

@app.route('/appointment/<int:appointment_id>', methods=['PUT'])
def update_appointment(appointment_id):
    appointment = Appointment.query.get_or_404(appointment_id)
    data = request.get_json()
    appointment.caregiver_user_id = data.get('caregiver_user_id', appointment.caregiver_user_id)
    appointment.member_user_id = data.get('member_user_id', appointment.member_user_id)
    appointment.appointment_date = data.get('appointment_date', appointment.appointment_date)
    appointment.appointment_time = data.get('appointment_time', appointment.appointment_time)
    appointment.work_hours = data.get('work_hours', appointment.work_hours)
    appointment.status = data.get('status', appointment.status)
    db.session.commit()
    return jsonify({'message': 'Appointment updated successfully'})

@app.route('/appointment/<int:appointment_id>', methods=['DELETE'])
def delete_appointment(appointment_id):
    appointment = Appointment.query.get_or_404(appointment_id)
    db.session.delete(appointment)
    db.session.commit()
    return jsonify({'message': 'Appointment deleted successfully'})



@app.route('/job', methods=['POST'])
def create_job():
    try:
        data = request.get_json()
        new_job = Job(
            job_id=data['job_id'],
            member_user_id=data['member_user_id'],
            required_caregiving_type=data['required_caregiving_type'],
            other_requirements=data['other_requirements'],
            date_posted=data['date_posted']
        )
        db.session.add(new_job)
        db.session.commit()
        return jsonify({'message': 'Job created successfully'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/jobs', methods=['GET'])
def get_jobs():
    jobs = Job.query.all()
    return jsonify([{
        'job_id': job.job_id,
        'member_user_id': job.member_user_id,
        'required_caregiving_type': job.required_caregiving_type,
        'other_requirements': job.other_requirements,
        'date_posted': job.date_posted
    } for job in jobs])


@app.route('/job/<int:job_id>', methods=['GET'])
def get_job(job_id):
    job = Job.query.get_or_404(job_id)
    return jsonify({
        'job_id': job.job_id,
        'member_user_id': job.member_user_id,
        'required_caregiving_type': job.required_caregiving_type,
        'other_requirements': job.other_requirements,
        'date_posted': job.date_posted
    })


@app.route('/job/<int:job_id>', methods=['PUT'])
def update_job(job_id):
    job = Job.query.get_or_404(job_id)
    data = request.get_json()
    job.member_user_id = data.get('member_user_id', job.member_user_id)
    job.required_caregiving_type = data.get('required_caregiving_type', job.required_caregiving_type)
    job.other_requirements = data.get('other_requirements', job.other_requirements)
    job.date_posted = data.get('date_posted', job.date_posted)
    db.session.commit()
    return jsonify({'message': 'Job updated successfully'})


@app.route('/job/<int:job_id>', methods=['DELETE'])
def delete_job(job_id):
    job = Job.query.get_or_404(job_id)
    db.session.delete(job)
    db.session.commit()
    return jsonify({'message': 'Job deleted successfully'})



@app.route('/job_application', methods=['POST'])
def create_job_application():
    try:
        data = request.get_json()
        new_job_application = JobApplication(
            caregiver_user_id=data['caregiver_user_id'],
            job_id=data['job_id'],
            date_applied=data['date_applied']
        )
        db.session.add(new_job_application)
        db.session.commit()
        return jsonify({'message': 'Job application created successfully'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/job_applications', methods=['GET'])
def get_job_applications():
    job_applications = JobApplication.query.all()
    return jsonify([{'caregiver_user_id': ja.caregiver_user_id, 'job_id': ja.job_id, 'date_applied': ja.date_applied} for ja in job_applications])


@app.route('/job_application/<int:caregiver_user_id>/<int:job_id>', methods=['GET'])
def get_job_application(caregiver_user_id, job_id):
    job_application = JobApplication.query.get_or_404((caregiver_user_id, job_id))
    return jsonify({'caregiver_user_id': job_application.caregiver_user_id, 'job_id': job_application.job_id, 'date_applied': job_application.date_applied})

@app.route('/job_application/<int:caregiver_user_id>/<int:job_id>', methods=['PUT'])
def update_job_application(caregiver_user_id, job_id):
    job_application = JobApplication.query.get_or_404((caregiver_user_id, job_id))
    data = request.get_json()
    job_application.date_applied = data.get('date_applied', job_application.date_applied)
    db.session.commit()
    return jsonify({'message': 'Job application updated successfully'})


@app.route('/job_application/<int:caregiver_user_id>/<int:job_id>', methods=['DELETE'])
def delete_job_application(caregiver_user_id, job_id):
    job_application = JobApplication.query.get_or_404((caregiver_user_id, job_id))
    db.session.delete(job_application)
    db.session.commit()
    return jsonify({'message': 'Job application deleted successfully'})



if __name__ == '__main__':
    app.run(debug=True)


