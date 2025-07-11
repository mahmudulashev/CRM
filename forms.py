from flask_wtf import FlaskForm
from wtforms import (
    StringField, SelectField, TextAreaField,
    IntegerField, DateField, SelectMultipleField
)
from wtforms.validators import DataRequired, Optional

class StudentForm(FlaskForm):
    fullname    = StringField('Ism',           validators=[DataRequired()])
    parent_name = StringField('Ota-ona ismi',  validators=[Optional()])
    phone1      = StringField('Telefon 1',     validators=[Optional()])
    phone2      = StringField('Telefon 2',     validators=[Optional()])
    phone3      = StringField('Telefon 3',     validators=[Optional()])
    status      = SelectField(
        'Status',
        choices=[('active','Active'),('left','Left'),('on-hold','On-hold')]
    )
    join_date   = DateField('Qo‘shilgan sana', validators=[Optional()])
    payment_day = IntegerField('Oylik kuni',   validators=[Optional()])
    comments    = TextAreaField('Komment',     validators=[Optional()])
    groups      = SelectMultipleField('Guruh(lar)', coerce=int)

class GroupForm(FlaskForm):
    name     = StringField(
        'Guruh nomi',
        validators=[DataRequired()]
    )
    schedule = StringField(
        'Dars kunlari (Mon,Wed,Fri)',
        validators=[DataRequired()]
    )
