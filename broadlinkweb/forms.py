from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length

class CommandForm(FlaskForm):
    command = StringField('Command', validators=[DataRequired(), Length(min=1, max=20)], id='command-input')
    submit = SubmitField('Learn command')