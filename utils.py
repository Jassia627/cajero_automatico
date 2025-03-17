# utils.py - Funciones de utilidad y validación para el cajero automático

import re
import random
from datetime import datetime, timedelta

def validar_numero_nequi(numero):
    """
    Valida si un número cumple con el formato para retiro NEQUI
    
    Args:
        numero (str): Número a validar
        
    Returns:
        bool: True si es válido, False en caso contrario
    """
    # Debe ser una cadena de 10 dígitos numéricos que empiece con 3
    return bool(re.match(r'^3\d{9}$', numero))

def validar_numero_ahorro_mano(numero):
    """
    Valida si un número cumple con el formato para retiro Ahorro a la Mano
    
    Args:
        numero (str): Número a validar
        
    Returns:
        bool: True si es válido, False en caso contrario
    """
    # Debe ser una cadena de 11 dígitos que empiece con 0 o 1 y el segundo dígito sea 3
    return bool(re.match(r'^[01]3\d{9}$', numero))

def validar_numero_cuenta_ahorros(numero):
    """
    Valida si un número cumple con el formato para retiro Cuenta de Ahorros
    
    Args:
        numero (str): Número a validar
        
    Returns:
        bool: True si es válido, False en caso contrario
    """
    # Debe ser una cadena de 11 dígitos numéricos
    return bool(re.match(r'^\d{11}$', numero))

def generar_clave_temporal(longitud=6):
    """
    Genera una clave temporal numérica
    
    Args:
        longitud (int): Longitud de la clave (por defecto 6)
        
    Returns:
        str: Clave temporal generada
    """
    return ''.join(random.choices('0123456789', k=longitud))

def calcular_tiempo_expiracion(segundos=60):
    """
    Calcula el tiempo de expiración para una clave temporal
    
    Args:
        segundos (int): Segundos hasta la expiración (por defecto 60)
        
    Returns:
        float: Timestamp de expiración
    """
    return (datetime.now() + timedelta(seconds=segundos)).timestamp()

def ha_expirado(timestamp_expiracion):
    """
    Verifica si un timestamp ha expirado
    
    Args:
        timestamp_expiracion (float): Timestamp de expiración
        
    Returns:
        bool: True si ha expirado, False en caso contrario
    """
    return datetime.now().timestamp() > timestamp_expiracion

def formato_moneda(valor):
    """
    Formatea un valor numérico como moneda colombiana
    
    Args:
        valor (int|str): Valor a formatear
        
    Returns:
        str: Valor formateado como moneda
    """
    try:
        # Asegurarse de que el valor sea un entero
        valor_int = int(valor)
        return "${:,.0f}".format(valor_int).replace(",", ".")
    except (ValueError, TypeError):
        return "$0"

def validar_monto_personalizado(monto_str):
    """
    Valida si un monto ingresado por el usuario es válido
    
    Args:
        monto_str (str): Monto como cadena de texto
        
    Returns:
        tuple: (bool, int|None, str|None) - (Es válido, monto convertido, mensaje de error)
    """
    try:
        monto = int(monto_str)
        if monto <= 0:
            return False, None, "El monto debe ser mayor que cero"
        
        if monto % 10000 != 0:
            return False, None, "El monto debe ser múltiplo de 10.000 pesos"
        
        if monto == 145000:
            return False, None, "No se permite el retiro de 145.000 pesos"
        
        return True, monto, None
    except ValueError:
        return False, None, "El monto debe ser un número válido"