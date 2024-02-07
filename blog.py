from flask import Flask,render_template,flash,redirect,url_for,session,logging,request
from flask_mysqldb import MySQL
from wtforms import Form,StringField,TextAreaField,PasswordField,validators
from passlib.hash import sha256_crypt 

# Kullanıcı Kayıt Formu

class RegisterForm(Form):
    name = StringField("İsim Soyisim",validators=[validators.Length(min=4,max=24)])
    username = StringField("Kullanıcı Adı",validators=[validators.Length(min=5,max=35)])
    email = StringField("Email Adresi",validators=[validators.Email(message="Lütfen Geçerli Bir Email Adresi Girin...")])
    password = PasswordField("Parola ",validators=[
        validators.DataRequired(message="Lütfen Bir Parola Belirleyin"),
        validators.EqualTo(fieldname="confirm",message="Parolanız Uyuşmuyor...")
    ])
    confirm=PasswordField("Parola Doğrula")
    
class LoginForm(Form):
    username=StringField("Kullanıcı Adı")
    password=PasswordField("Parola")


app = Flask(__name__)
app.secret_key="ybblog"

app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = ""
app.config["MYSQL_DB"] = "ybblog"
app.config["MYSQL_CURSORCLASS"]="DictCursor"

mysql = MySQL(app)


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/about')
def about():
    return render_template("about.html")

#Kayıt olma

@app.route('/register',methods=["GET","POST"])
def register():
    
    form= RegisterForm(request.form)
    if request.method=="POST" and form.validate():
        name = form.name.data
        username = form.username.data
        email = form.email.data
        password = sha256_crypt.encrypt(form.password.data)
        
        cursor = mysql.connection.cursor()
        
        sorgu ="Insert into users(name,email,username,password) VALUES (%s,%s,%s,%s)"
        
        cursor.execute(sorgu,(name,email,username,password))
        
        mysql.connection.commit()
        cursor.close()
        
        flash("Başarıyla Kayıt Oldunuz...","success")
        return redirect(url_for("login"))
    else: 
        return render_template('register.html',form=form)

@app.route('/login',methods=["GET","POST"])
def login():
    form=LoginForm(request.form)
    if request.method=="POST":
        username=form.username.data
        password_entered=form.password.data
        
        cursor = mysql.connection.cursor()
        
        sorgu = "Select * From users where username = %s"
        result = cursor.execute(sorgu,(username,))
        if result > 0:
            data=cursor.fetchone()
            real_password=data["password"]
            if sha256_crypt.verify(password_entered,real_password):
                flash("Giriş Yaptınız...","success")
                return redirect(url_for("index"))
            else:
                flash("Şifreyi Yanlış Girdiniz...","danger")
                return redirect(url_for("login"))
        else:
            flash("Böyle Bir Kullanıcı Bulunmuyor...","danger")
            return redirect(url_for("login"))
    return render_template('login.html',form = form)
if __name__ =="__main__":
    app.run(debug=True)

