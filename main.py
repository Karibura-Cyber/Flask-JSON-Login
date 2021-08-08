from flask import Flask, flash, request, redirect, render_template
from werkzeug.utils import secure_filename
import os
import os
import json
import base64
import time


if not os.path.exists('data'):
    os.makedirs('data')


app=Flask(__name__)

app.secret_key = "secret key"
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

path = os.getcwd()
# file Upload
UPLOAD_FOLDER = os.path.join(path, 'static/uploads')

if not os.path.isdir(UPLOAD_FOLDER):
    os.mkdir(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS





@app.route('/')
def home():
    return 'Index Page'

  
@app.route('/signin')
def signin():
    return render_template('signin.html')

@app.route('/signin', methods=['POST'])
def signin_post():
    name = request.form['name']
    passwd = request.form['passwd']
    
    passwd_bytes = passwd.encode('ascii')
    base64_bytes = base64.b64encode(passwd_bytes)
    base64_passwd = base64_bytes.decode('ascii')

    #os check file
    if os.path.exists('data/{}_data.json'.format(name)):
        with open('data/{}_data.json'.format(name), 'r') as f:
            i = json.load(f)
            
    elif not os.path.exists('data/{}_data.json'.format(name)):
        return 'user not found'

    if i["username"] == name and i["passwd"] == base64_passwd:
        return  "<script>window.location.href = '/userinfo/{}';</script>".format(name)
    else:
        return 'Invalid username or password <a href="/signin">Sign In</a>'
   
    



@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/signup', methods=['POST'])
def signup_post():
    name = request.form['name']
    passwd = request.form['passwd']
    
    passwd_bytes = passwd.encode('ascii')
    base64_bytes = base64.b64encode(passwd_bytes)
    base64_passwd = base64_bytes.decode('ascii')


    #os search file
    if os.path.exists('data/{}_data.json'.format(name)):
        return 'user already exists <a href="/signup">Sign Up</a>'
    elif not os.path.exists('data/{}_data.json'.format(name)):
        with open('data/{}_data.json'.format(name), 'w') as outfile:
            json.dump({'username': name, 'passwd': base64_passwd, 'img': 'uploads/{}.jpg'.format(name), 'score': 0}, outfile)

       
       
    return  "<script>window.location.href = '/signin';</script>"


@app.route('/userinfo/<name>')
def userinfo(name):
    if os.path.exists('data/{}_data.json'.format(name)):
        with open('data/{}_data.json'.format(name), 'r') as f:
            i = json.load(f)
            
    elif not os.path.exists('data/{}_data.json'.format(name)):
        return 'user not found'
    if i["score"] < 0:
        score = 'Error'
    else:
        score = i["score"]
        img = i["img"]
    return render_template('userinfo.html', name=name, score=score, img=img)

@app.route('/userinfo/upload/<name>')
def upload_form(name):
    return render_template('upload.html', name=name)


@app.route('/userinfo/upload/<name>', methods=['POST'])
def upload_file(name):
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No file selected for uploading')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            flash('File successfully uploaded')
            #os rename file
            os.rename(os.path.join(app.config['UPLOAD_FOLDER'], filename), os.path.join(app.config['UPLOAD_FOLDER'], '{}.jpg'.format(name)))
            return redirect('/userinfo/{}'.format(name))
        else:
            flash('Allowed file types are txt, pdf, png, jpg, jpeg, gif')
            return redirect(request.url)

@app.route('/api/<name>')
def api(name):
    if os.path.exists('data/{}_data.json'.format(name)):
        with open('data/{}_data.json'.format(name), 'r') as f:
            i = json.load(f)
    
    return json.dumps({'username': i["username"], 'score': i["score"]})




if __name__ == '__main__':
    app.run(debug=True)