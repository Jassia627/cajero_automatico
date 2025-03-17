# billetes.py - Lógica para cálculo de billetes y validación de montos

# Definición de los billetes disponibles
billetes = [
    {'billete': '10k', 'valor': 10000, 'img': '10k.png'},
    {'billete': '20k', 'valor': 20000, 'img': '20k.png'},
    {'billete': '50k', 'valor': 50000, 'img': '50k.png'},
    {'billete': '100k', 'valor': 100000, 'img': '100k.png'}
]

def monto_valido(monto):
    """
    Verifica si un monto es válido para retiro.
    
    Args:
        monto (int): El monto a verificar
        
    Returns:
        bool: True si el monto es válido, False en caso contrario
    """
    return monto > 0 and monto % 10000 == 0

def mostrar_matriz(cantidad):
    """
    Genera la matriz de acarreo para un monto dado.
    
    Args:
        cantidad (int): El monto a retirar
        
    Returns:
        list: Matriz de acarreo o lista vacía si el monto no es válido
    """
    if not monto_valido(cantidad):
        print('La cantidad debe ser un múltiplo de 10000 y positivo')
        return []

    matriz = []
    suma = 0
    alcanzado = False
    total_rows = 0

    while not alcanzado:
        fila = [0] * total_rows
        se_pudo_sumar = False
        suma_temporal = suma

        for j in range(total_rows, len(billetes)):
            if suma_temporal + billetes[j]['valor'] <= cantidad:
                fila.append(1)
                suma_temporal += billetes[j]['valor']
                se_pudo_sumar = True

                if suma_temporal == cantidad:
                    alcanzado = True
                    suma = suma_temporal
                    break
            else:
                fila.append(0)

        suma = suma_temporal
        matriz.append(fila)

        if not se_pudo_sumar and all(v == 0 for v in fila[total_rows:]):
            if any(v == 1 for v in fila[total_rows:]):
                total_rows += 1
            else:
                total_rows = 0
        else:
            total_rows += 1

    return matriz

def calcular_billetes_acarreo(matriz):
    """
    Calcula los billetes a entregar a partir de la matriz de acarreo.
    
    Args:
        matriz (list): Matriz de acarreo generada por mostrar_matriz
        
    Returns:
        list: Lista de billetes a entregar
    """
    billetes_entrega = []

    for i, fila in enumerate(matriz):
        for j, valor in enumerate(fila):
            if valor == 1:
                billetes_entrega.append(billetes[j])

    return billetes_entrega

def calcular_billetes(monto):
    """
    Calcula la cantidad de billetes necesarios para un monto dado.
    
    Args:
        monto (int): Monto a retirar
        
    Returns:
        dict: Diccionario con la cantidad de cada billete o None si no es posible
    """
    if not monto_valido(monto):
        return None

    # Generar matriz de acarreo
    matriz = mostrar_matriz(monto)
    if not matriz:
        return None

    # Obtener billetes usando la matriz
    billetes_resultado = calcular_billetes_acarreo(matriz)

    # Convertir al formato esperado por la aplicación
    resultado = {
        100000: 0,
        50000: 0,
        20000: 0,
        10000: 0
    }

    # Contar la cantidad de cada tipo de billete
    for billete in billetes_resultado:
        resultado[billete['valor']] += 1

    return resultado

def predecir_retiros(transacciones, num_predicciones=5):
    """
    Predice los próximos montos probables de retiro basado en el historial.
    
    Args:
        transacciones (list): Lista de transacciones previas
        num_predicciones (int): Número de predicciones a retornar
        
    Returns:
        list: Lista de montos predichos ordenados por frecuencia
    """
    if not transacciones:
        return []
        
    # Contar frecuencia de montos
    frecuencias = {}
    for trans in transacciones:
        monto = trans.get('monto', 0)
        frecuencias[monto] = frecuencias.get(monto, 0) + 1
    
    # Ordenar por frecuencia y obtener los top N
    montos_ordenados = sorted(frecuencias.items(), key=lambda x: (-x[1], -x[0]))
    return [monto for monto, _ in montos_ordenados[:num_predicciones]]

# Función de utilidad para comprobar el funcionamiento del algoritmo
def test_acarreo(monto):
    """
    Función de prueba para verificar el algoritmo de acarreo.
    
    Args:
        monto (int): Monto a probar
        
    Returns:
        None: Imprime los resultados en consola
    """
    print(f"Probando acarreo para monto: {monto}")
    
    if not monto_valido(monto):
        print(f"Monto inválido: {monto}")
        return
    
    matriz = mostrar_matriz(monto)
    print("Matriz de acarreo:")
    for fila in matriz:
        print(" ".join(map(str, fila)))
    
    billetes_resultado = calcular_billetes_acarreo(matriz)
    print("\nBilletes a entregar:")
    for billete in billetes_resultado:
        print(f"Billete de {billete['billete']}: {billete['valor']}")
    
    total = sum(b['valor'] for b in billetes_resultado)
    print(f"\nTotal: {total}")
    
    # Versión compatible con la aplicación
    resultado_app = calcular_billetes(monto)
    print("\nResultado para la aplicación:")
    for valor, cantidad in resultado_app.items():
        if cantidad > 0:
            print(f"{cantidad} billetes de {valor}")


# Si el archivo se ejecuta directamente, realizar pruebas
if __name__ == "__main__":
    # Ejemplos de prueba
    test_acarreo(180000)
    print("\n" + "-"*50 + "\n")
    test_acarreo(230000)