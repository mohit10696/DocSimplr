from flask import Flask, render_template, request, redirect, url_for,flash
import os
import resumeMatcher

# UPLOAD_FOLDER = '/path/to/the/uploads'
ALLOWED_EXTENSIONS = {'zip'}

application = app = Flask(__name__)
app.secret_key =os.urandom(12)

@app.route('/')
def index():
   return render_template("index.html")
 
@app.route('/fileUpload.html')
def upload():
	return render_template("fileUpload.html")

@app.route('/index.html')
# @exception_handler
def indexRedirect():
    return render_template("index.html")

@app.route('/about.html')
def about():
    return render_template("about.html")

@app.route('/services.html')
def services():
    return render_template("services.html")

@app.route('/feedback.html')
def feedback():
    return render_template("feedback.html")

@app.route('/contact.html')
def contact():
    return render_template("contact.html")

@app.route('/file', methods=['GET', 'POST'])
def handleFileUpload():
    if request.method == "POST":
    	file=request.files['uploadResume']
    	email=request.form['email']
    	if file.filename != '':
    		filePath=os.path.join('./UploadedResume',file.filename)
    		file.save(filePath)
    	if len(email)>0:
    		resumeMatcher.process(filePath,email)

    flash("Email Has been sent!")      
    return render_template('index.html')
 
if __name__ == '__main__':
   app.run(debug=True)
