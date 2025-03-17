from flask import Flask, render_template, request, redirect, url_for, flash, session
import os
from datetime import datetime

# Importar módulos personalizados
from billetes import calcular_billetes, mostrar_matriz, predecir_retiros
from db import usuarios, OPCIONES_RETIRO, transacciones, guardar_transaccion, actualizar_saldo, obtener_saldo
from utils import (validar_numero_nequi, validar_numero_ahorro_mano, validar_numero_cuenta_ahorros, 
                  generar_clave_temporal, calcular_tiempo_expiracion, ha_expirado, formato_moneda,
                  validar_monto_personalizado)

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'clave_secreta_cajero_automatico')

# Configuración de carpetas estáticas
app.static_folder = 'static'
app.template_folder = 'templates'

# Rutas de la aplicación
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/seleccionar_tipo')
def seleccionar_tipo():
    return render_template('seleccionar_tipo.html')

# Ruta para retiro tipo NEQUI
@app.route('/nequi', methods=['GET', 'POST'])
def nequi():
    if request.method == 'POST':
        numero = request.form.get('numero', '')
        
        # Validar formato (10 dígitos, solo números)
        if not validar_numero_nequi(numero):
            flash('El número debe contener exactamente 10 dígitos numéricos y empezar con 3', 'error')
            return render_template('nequi.html')
        
        # Verificar si el usuario existe
        if numero in usuarios and usuarios[numero]['tipo'] == 'nequi':
            # Guardar el número original en la sesión
            session['usuario'] = numero
            session['tipo_cuenta'] = 'nequi'
            return redirect(url_for('seleccionar_monto'))
        else:
            flash('Usuario no encontrado', 'error')
            return render_template('nequi.html')
    
    return render_template('nequi.html')

# Ruta para retiro tipo Ahorro a la Mano
@app.route('/ahorro_mano', methods=['GET', 'POST'])
def ahorro_mano():
    if request.method == 'POST':
        numero = request.form.get('numero', '')
        clave = request.form.get('clave', '')
        
        # Validar formato (11 dígitos, empieza con 0 o 1, segundo dígito es 3)
        if not validar_numero_ahorro_mano(numero):
            flash('El número debe ser de 11 dígitos, empezar con 0 o 1, y el segundo dígito debe ser 3', 'error')
            return render_template('ahorro_mano.html')
        
        # Verificar si el usuario existe y la clave es correcta
        if numero in usuarios and usuarios[numero]['tipo'] == 'ahorro_mano' and usuarios[numero]['clave'] == clave:
            session['usuario'] = numero
            session['tipo_cuenta'] = 'ahorro_mano'
            return redirect(url_for('seleccionar_monto'))
        else:
            flash('Usuario o clave incorrectos', 'error')
            return render_template('ahorro_mano.html')
    
    return render_template('ahorro_mano.html')

# Ruta para retiro tipo Cuenta de Ahorros
@app.route('/cuenta_ahorros', methods=['GET', 'POST'])
def cuenta_ahorros():
    if request.method == 'POST':
        numero = request.form.get('numero', '')
        clave = request.form.get('clave', '')
        
        # Validar formato (11 dígitos, solo números)
        if not validar_numero_cuenta_ahorros(numero):
            flash('El número debe contener exactamente 11 dígitos numéricos', 'error')
            return render_template('cuenta_ahorros.html')
        
        # Verificar si el usuario existe y la clave es correcta
        if numero in usuarios and usuarios[numero]['tipo'] == 'cuenta_ahorros' and usuarios[numero]['clave'] == clave:
            session['usuario'] = numero
            session['tipo_cuenta'] = 'cuenta_ahorros'
            return redirect(url_for('seleccionar_monto'))
        else:
            flash('Usuario o clave incorrectos', 'error')
            return render_template('cuenta_ahorros.html')
    
    return render_template('cuenta_ahorros.html')

# Seleccionar monto a retirar
@app.route('/seleccionar_monto', methods=['GET', 'POST'])
def seleccionar_monto():
    if 'usuario' not in session:
        flash('Debe iniciar sesión primero', 'error')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        usuario = session['usuario']
        monto_str = request.form.get('monto', '')
        
        # Si no es un monto predefinido, validar el monto personalizado
        if monto_str not in map(str, OPCIONES_RETIRO):
            es_valido, monto, mensaje = validar_monto_personalizado(monto_str)
            if not es_valido:
                flash(mensaje, 'error')
                return redirect(url_for('seleccionar_monto'))
        else:
            monto = int(monto_str)
        
        # Verificar saldo suficiente
        if monto > usuarios[usuario]['saldo']:
            flash('Saldo insuficiente', 'error')
            return redirect(url_for('seleccionar_monto'))
        
        # Calcular billetes
        billetes = calcular_billetes(monto)
        if not billetes:
            flash('No es posible entregar ese monto con los billetes disponibles', 'error')
            return redirect(url_for('seleccionar_monto'))
        
        # Si es Nequi, generar clave temporal y redirigir
        if session['tipo_cuenta'] == 'nequi':
            # Guardar información del retiro en la sesión
            session['monto_retiro'] = monto
            session['billetes_retiro'] = billetes
            
            # Generar clave temporal
            clave_temporal = generar_clave_temporal()
            expiracion = calcular_tiempo_expiracion()
            session['clave_temporal'] = clave_temporal
            session['expiracion'] = expiracion
            
            return render_template('clave_temporal.html', clave=clave_temporal)
        
        # Para otros tipos de cuenta, proceder directamente
        actualizar_saldo(usuario, monto)
        guardar_transaccion(usuario, monto, session['tipo_cuenta'])
        
        # Obtener la fecha actual formateada
        fecha_actual = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        
        return render_template('resultado_retiro.html', 
                             monto=monto, 
                             billetes=billetes, 
                             saldo=usuarios[usuario]['saldo'],
                             fecha_actual=fecha_actual)
    
    return render_template('seleccionar_monto.html', opciones=OPCIONES_RETIRO)

@app.route('/verificar_clave_temporal', methods=['POST'])
def verificar_clave_temporal():
    if 'clave_temporal' not in session or 'expiracion' not in session:
        flash('Sesión inválida', 'error')
        return redirect(url_for('nequi'))
    
    if ha_expirado(session['expiracion']):
        flash('La clave temporal ha expirado', 'error')
        return redirect(url_for('nequi'))
    
    clave_ingresada = request.form.get('clave', '')
    if clave_ingresada == session['clave_temporal']:
        usuario = session['usuario']
        monto = session['monto_retiro']
        billetes = session['billetes_retiro']
        
        # Actualizar saldo y registrar transacción
        actualizar_saldo(usuario, monto)
        guardar_transaccion(usuario, monto, session['tipo_cuenta'])
        
        # Limpiar variables de sesión temporales
        session.pop('monto_retiro', None)
        session.pop('billetes_retiro', None)
        session.pop('clave_temporal', None)
        session.pop('expiracion', None)
        
        # Obtener la fecha actual formateada
        fecha_actual = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        
        return render_template('resultado_retiro.html', 
                             monto=monto, 
                             billetes=billetes, 
                             saldo=usuarios[usuario]['saldo'],
                             fecha_actual=fecha_actual)
    else:
        flash('Clave temporal incorrecta', 'error')
        return redirect(url_for('seleccionar_monto'))

# Cerrar sesión
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

# Página de error 404
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

# Filtro para formato de moneda
@app.template_filter('moneda')
def filtro_moneda(valor):
    return formato_moneda(valor)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))