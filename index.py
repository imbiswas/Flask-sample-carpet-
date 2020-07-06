import manager
import uuid
import os
from flask import Flask, flash, request, redirect, url_for,jsonify, render_template
from werkzeug.utils import secure_filename
from wtforms import Form, TextField, TextAreaField, validators, StringField, SubmitField
import mydatabase

UPLOAD_FOLDER = 'images/'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

DEBUG = True
app = Flask(__name__)
app.config.from_object(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


class ReusableForm(Form):
    lenght = TextField('lenght:', validators=[validators.required()])
    bredth = TextField('bredth:', validators=[validators.required(), validators.Length(min=6, max=35)])
    no_of_colors = TextField('no_of_colors:', validators=[validators.required(), validators.Length(min=3, max=35)])


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/", methods=['GET', 'POST'])
def home():
    form = ReusableForm(request.form)
 
# print form.errors
    if request.method == 'POST':
        lenght=float(request.form['lenght'])
        bredth=float(request.form['bredth'])
        no_of_colors=int(request.form['no_of_colors'])

        ##############################################
        if 'file' not in request.files:
            flash('No file part')
        file = request.files['image']
        # if user does not select file, browser also
        # submit an empty part without filename

        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = str(uuid.uuid4())
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                                    

        image=UPLOAD_FOLDER+filename

        image=UPLOAD_FOLDER+filename
        result = manager.manager(lenght, bredth, image, no_of_colors).valueTaker()
        area=float(result[1])
        tasks = []
        for values in result[0]:
            percent=values[0]
            percentNum = str(percent[:-1])
            color=values[1]
            hashVal=values[2]
            areaPercent=float(percentNum)*area/100
            

            task1=[
                {
                    'percent':percent,
                    'color':color,
                    'hash':hashVal,
                    'areaPercent':areaPercent,

                },
            ]
            tasks.append(task1)
            # print(tasks)
        database=mydatabase.databse().material()
        final=[tasks,database]
        
        return render_template('result.html', my_objects=final)
    
    if form.validate():
    # Save the comment here.
        flash('Thanks for registration ')
    else:
        flash('Error: All the form fields are required. ')
    
    return render_template('hello.html', form=form)


@app.route('/api', methods=['POST'])
def get_tasks():
    lenght = float(request.form['lenght'])
    bredth = float(request.form['bredth'])
    # check if the post request has the file part
    if 'file' not in request.files:
        flash('No file part')
    file = request.files['image']
    # if user does not select file, browser also
    # submit an empty part without filename

    if file.filename == '':
        flash('No selected file')
        # return redirect(request.url)

    if file and allowed_file(file.filename):
        filename = str(uuid.uuid4())
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        # return redirect(url_for('uploaded_file',
                                # filename=filename))

    image=UPLOAD_FOLDER+filename
    no_of_colors = int(request.form['no_of_colors'])
    result = manager.manager(lenght, bredth, image, no_of_colors).valueTaker()
    area=float(result[1])
    tasks = []
    for values in result[0]:
        percent=values[0]
        percentNum = str(percent[:-1])
        color=values[1]
        hashVal=values[2]
        areaPercent=float(percentNum)*area/100

        task1=[
            {
                'percent':percent,
                'color':color,
                'hash':hashVal,
                'areaPercent':areaPercent,

            },
        ]
        tasks.append(task1)
    return jsonify({'tasks': tasks})
            
if __name__ == '__main__':
    app.secret_key = 'super secret key'
    app.run(port=5555,host="0.0.0.0")