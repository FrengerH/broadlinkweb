from flask import redirect, url_for, render_template, flash
from broadlinkweb.broadlink import Broadlink
from broadlinkweb.forms import CommandForm
from broadlinkweb import exceptions
from broadlinkweb import app

@app.route('/', methods=['GET', 'POST'])
def index(deviceName=None):
    form = CommandForm()
    devices = Broadlink().getDevices()
    return render_template('index.html', devices=devices, form=form)

@app.route('/search', methods=['GET'])
def search():
    Broadlink().searchDevices()
    return redirect(url_for('index'))

@app.route('/learn/<deviceName>', methods=['POST'])
def learn(deviceName):
    form = CommandForm()
    if form.validate_on_submit() and deviceName:
        Broadlink().learn(deviceName, form.command.data)
        flash('Command learned', 'success')
    return redirect(url_for('index'))

@app.route('/send/<deviceName>/<command>', methods=['get'])
def send(deviceName, command):
    Broadlink().send(deviceName, command)
    flash('Command send', 'success')
    return redirect(url_for('index'))

@app.route('/deletecommand/<deviceName>/<command>', methods=['GET'])
def deleteCommand(deviceName, command):
    Broadlink().deleteCommand(deviceName, command)
    flash('Command deleted', 'success')
    return redirect(url_for('index'))

@app.route('/deletedevice/<deviceName>', methods=['GET'])
def deleteDevice(deviceName):
    Broadlink().deleteDevice(deviceName)
    flash('Device deleted', 'success')
    return redirect(url_for('index'))

@app.errorhandler(Exception)
def handleException(error):
    flash(str(error), 'danger')
    return render_template('error.html')

@app.errorhandler(exceptions.AppException)
def handleAppException(error):
    flash(str(error), 'danger')
    return redirect(url_for('index'))