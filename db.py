

# Simulación de base de datos
usuarios = {
    # Estilo NEQUI (10 dígitos)
    '3001234567': {'clave': '123456', 'saldo': 2000000, 'tipo': 'nequi'},
    '3109876543': {'clave': '654321', 'saldo': 1500000, 'tipo': 'nequi'},
    '3204567890': {'clave': '112233', 'saldo': 1800000, 'tipo': 'nequi'},
    
    # Ahorro a la mano (11 dígitos, empezando con 0 o 1, segundo dígito 3)
    '03123456789': {'clave': '4321', 'saldo': 1200000, 'tipo': 'ahorro_mano'},
    '13987654321': {'clave': '1234', 'saldo': 800000, 'tipo': 'ahorro_mano'},
    '03345678901': {'clave': '5678', 'saldo': 900000, 'tipo': 'ahorro_mano'},
    
    # Cuenta de ahorros (11 dígitos)
    '11122334455': {'clave': '9876', 'saldo': 3000000, 'tipo': 'cuenta_ahorros'},
    '99988776655': {'clave': '6789', 'saldo': 2500000, 'tipo': 'cuenta_ahorros'},
    '12345678901': {'clave': '4567', 'saldo': 1700000, 'tipo': 'cuenta_ahorros'}
}

# Opciones fijas de retiro
OPCIONES_RETIRO = [20000, 50000, 100000, 200000, 600000]

# Registro de transacciones
transacciones = []

def guardar_transaccion(usuario, monto, tipo_cuenta):
    """
    Guarda una transacción en el registro
    
    Args:
        usuario (str): ID del usuario
        monto (int): Monto retirado
        tipo_cuenta (str): Tipo de cuenta usado para el retiro
        
    Returns:
        None
    """
    from datetime import datetime
    
    transacciones.append({
        'usuario': usuario,
        'monto': monto,
        'fecha': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'tipo_cuenta': tipo_cuenta
    })

def actualizar_saldo(usuario, monto):
    """
    Actualiza el saldo de un usuario después de un retiro
    
    Args:
        usuario (str): ID del usuario
        monto (int): Monto a retirar
        
    Returns:
        bool: True si la operación fue exitosa, False en caso contrario
    """
    if usuario not in usuarios:
        return False
    
    if usuarios[usuario]['saldo'] < monto:
        return False
    
    usuarios[usuario]['saldo'] -= monto
    return True

def verificar_usuario(numero, tipo):
    """
    Verifica si existe un usuario con el número y tipo especificados
    
    Args:
        numero (str): Número de cuenta o celular
        tipo (str): Tipo de cuenta (nequi, ahorro_mano, cuenta_ahorros)
        
    Returns:
        bool: True si el usuario existe, False en caso contrario
    """
    return numero in usuarios and usuarios[numero]['tipo'] == tipo

def verificar_clave(numero, clave):
    """
    Verifica si la clave ingresada es correcta para el usuario
    
    Args:
        numero (str): Número de cuenta o celular
        clave (str): Clave ingresada
        
    Returns:
        bool: True si la clave es correcta, False en caso contrario
    """
    return numero in usuarios and usuarios[numero]['clave'] == clave

def obtener_saldo(usuario):
    """
    Obtiene el saldo actual de un usuario
    
    Args:
        usuario (str): ID del usuario
        
    Returns:
        int: Saldo actual o None si el usuario no existe
    """
    if usuario in usuarios:
        return usuarios[usuario]['saldo']
    return None