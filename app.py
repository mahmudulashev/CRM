from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import date
from calendar import monthrange

from models import db, Student, Group, Attendance, Homework
from forms  import StudentForm, GroupForm

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']        = 'sqlite:///school_crm.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY']                     = 'verysecret'

db.init_app(app)
migrate = Migrate(app, db)


@app.route('/')
def index():
    return redirect(url_for('students'))


# ----------------- STUDENTS -----------------
@app.route('/students')
def students():
    form = StudentForm()
    form.groups.choices = [(g.id, g.name) for g in Group.query.all()]

    q         = request.args.get('q', '')
    statuses  = request.args.getlist('status')
    group_ids = request.args.getlist('group', type=int)

    query = Student.query
    if q:
        query = query.filter(Student.fullname.ilike(f"%{q}%"))
    if statuses:
        query = query.filter(Student.status.in_(statuses))
    if group_ids:
        query = query.join(Student.groups).filter(Group.id.in_(group_ids))

    students = query.all()
    groups   = Group.query.all()
    return render_template(
        'students.html',
        students  = students,
        groups    = groups,
        form      = form,
        q         = q,
        statuses  = statuses,
        group_ids = group_ids
    )


@app.route('/student/add', methods=['POST'])
def add_student():
    form = StudentForm()
    form.groups.choices = [(g.id, g.name) for g in Group.query.all()]
    if form.validate_on_submit():
        s = Student(
            fullname    = form.fullname.data,
            parent_name = form.parent_name.data,
            phone1      = form.phone1.data,
            phone2      = form.phone2.data,
            phone3      = form.phone3.data,
            status      = form.status.data,
            join_date   = form.join_date.data,
            payment_day = form.payment_day.data,
            comments    = form.comments.data
        )
        for gid in form.groups.data:
            s.groups.append(Group.query.get(gid))
        db.session.add(s)
        db.session.commit()
        flash('O‘quvchi qo‘shildi!', 'success')
    else:
        flash('Forma xatolik bilan to‘ldirilgan!', 'danger')
    return redirect(url_for('students'))


@app.route('/student/<int:id>/json')
def get_student_json(id):
    s = Student.query.get_or_404(id)
    return jsonify({
        'id'         : s.id,
        'fullname'   : s.fullname,
        'parent_name': s.parent_name,
        'phone1'     : s.phone1,
        'phone2'     : s.phone2,
        'phone3'     : s.phone3,
        'status'     : s.status,
        'join_date'  : s.join_date.isoformat() if s.join_date else '',
        'payment_day': s.payment_day,
        'comments'   : s.comments,
        'groups'     : [g.id for g in s.groups]
    })


@app.route('/student/<int:id>/edit', methods=['POST'])
def edit_student(id):
    student = Student.query.get_or_404(id)
    form = StudentForm()
    form.groups.choices = [(g.id, g.name) for g in Group.query.all()]
    if form.validate_on_submit():
        student.fullname    = form.fullname.data
        student.parent_name = form.parent_name.data
        student.phone1      = form.phone1.data
        student.phone2      = form.phone2.data
        student.phone3      = form.phone3.data
        student.status      = form.status.data
        student.join_date   = form.join_date.data
        student.payment_day = form.payment_day.data
        student.comments    = form.comments.data
        student.groups      = [Group.query.get(gid) for gid in form.groups.data]
        db.session.commit()
        flash('O‘quvchi yangilandi!', 'success')
    else:
        flash('Forma xatolik bilan to‘ldirilgan!', 'danger')
    return redirect(url_for('students'))


@app.route('/student/<int:id>/delete', methods=['POST'])
def delete_student(id):
    s = Student.query.get_or_404(id)
    db.session.delete(s)
    db.session.commit()
    flash('O‘quvchi o‘chirildi!', 'warning')
    return redirect(url_for('students'))


@app.route('/student/<int:id>')
def student_detail(id):
    student = Student.query.get_or_404(id)
    return render_template('student_detail.html', student=student)


# ----------------- GROUPS -----------------
@app.route('/groups')
def groups():
    form   = GroupForm()
    groups = Group.query.all()
    return render_template('groups.html', groups=groups, form=form)


@app.route('/group/add', methods=['POST'])
def add_group():
    form = GroupForm()
    if form.validate_on_submit():
        g = Group(name=form.name.data, schedule=form.schedule.data)
        db.session.add(g)
        db.session.commit()
        flash('Guruh qo‘shildi!', 'success')
    else:
        flash('Guruh qo‘shishda xatolik!', 'danger')
    return redirect(url_for('groups'))


@app.route('/group/<int:id>/json')
def get_group_json(id):
    g = Group.query.get_or_404(id)
    return jsonify({'id': g.id, 'name': g.name, 'schedule': g.schedule})


@app.route('/group/<int:id>/edit', methods=['POST'])
def edit_group(id):
    form = GroupForm()
    if form.validate_on_submit():
        g = Group.query.get_or_404(id)
        g.name     = form.name.data
        g.schedule = form.schedule.data
        db.session.commit()
        flash('Guruh yangilandi!', 'success')
    else:
        flash('Guruh tahrirlashda xatolik!', 'danger')
    return redirect(url_for('groups'))


@app.route('/group/<int:id>/delete', methods=['POST'])
def delete_group(id):
    g = Group.query.get_or_404(id)
    db.session.delete(g)
    db.session.commit()
    flash('Guruh o‘chirildi!', 'warning')
    return redirect(url_for('groups'))


@app.route('/group/<int:group_id>')
def group_detail(group_id):
    group    = Group.query.get_or_404(group_id)
    students = group.students
    return render_template(
        'group_detail.html',
        group=group,
        students=students
    )


# ----------------- ATTENDANCE MATRIX + AVERAGE + N/A -----------------
@app.route('/group/<int:group_id>/attendance_matrix', methods=['GET','POST'])
def attendance_matrix(group_id):
    group    = Group.query.get_or_404(group_id)
    students = group.students

    # 1) Yil/oyni olamiz
    today         = date.today()
    year          = int(request.args.get('year', today.year))
    month         = int(request.args.get('month', today.month))
    days_in_month = monthrange(year, month)[1]

    # 2) Guruh jadvalidagi haftaning kunlari
    wk_map = {'Mon':0,'Tue':1,'Wed':2,'Thu':3,'Fri':4,'Sat':5,'Sun':6}
    wanted = [wk_map[s.strip()] for s in group.schedule.split(',') if s.strip() in wk_map]
    days   = [
        date(year, month, d)
        for d in range(1, days_in_month+1)
        if date(year, month, d).weekday() in wanted
    ]

    if request.method=='POST':
        for s in students:
            for d in days:
                sid  = str(s.id)
                dstr = d.isoformat()

                #   3a) Attendance upsert
                attended = request.form.get(f'attend_{sid}_{dstr}')=='on'
                att = Attendance.query.filter_by(
                    date=d, student_id=s.id, group_id=group.id
                ).first()
                if not att:
                    att = Attendance(date=d, status=attended,
                                     student_id=s.id, group_id=group.id)
                    db.session.add(att)
                else:
                    att.status = attended

                #   3b) Homework upsert: N/A opsiyasi uchun value="na"
                raw = request.form.get(f'homework_{sid}_{dstr}')
                # agar raw=='na' yoki bo‘sh bo‘lsa → o‘chirib tashlaymiz
                hw = Homework.query.filter_by(
                    date=d, student_id=s.id, group_id=group.id
                ).first()
                if raw in (None, '', 'na'):
                    if hw:
                        db.session.delete(hw)
                else:
                    percent = int(raw)
                    if not hw:
                        hw = Homework(date=d, percent_done=percent,
                                      student_id=s.id, group_id=group.id)
                        db.session.add(hw)
                    else:
                        hw.percent_done = percent

        db.session.commit()
        flash("Oylik davomat va uy ishi saqlandi!", "success")
        return redirect(url_for(
            'attendance_matrix',
            group_id=group.id,
            year=year,
            month=month
        ))

    # 4) GET: mavjud yozuvlarni yuklab olamiz
    att_map = {
        (a.student_id, a.date): a
        for a in Attendance.query.filter(
            Attendance.group_id==group.id,
            Attendance.date.between(days[0], days[-1])
        )
    }
    hw_map = {
        (h.student_id, h.date): h
        for h in Homework.query.filter(
            Homework.group_id==group.id,
            Homework.date.between(days[0], days[-1])
        )
    }

    # 5) O‘rtacha uy ishi foizini hisoblaymiz (faqat N/A bo‘lmagan kunlar)
    avg_hw = {}
    for s in students:
        total = 0
        count = 0
        for d in days:
            h = hw_map.get((s.id, d))
            if h is not None:    # faqat mavjud (ya’ni “na” bo‘lmagan)
                total += h.percent_done
                count += 1
        avg_hw[s.id] = round(total/count,1) if count else None

    return render_template(
        'attendance_matrix.html',
        group    = group,
        students = students,
        days     = days,
        att_map  = att_map,
        hw_map   = hw_map,
        avg_hw   = avg_hw,
        year     = year,
        month    = month
    )


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
