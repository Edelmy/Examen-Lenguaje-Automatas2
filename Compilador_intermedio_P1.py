import re #Se importa la libreria del regex

PRECEDENCE = {'+': 1, '-': 1, '*': 2, '/': 2, '^': 3} #Prioridad de las operaciones
PRECEDENCE['~'] = 2.5 # '~' representa el menos unario (-a) Se resuelve antes que + y -
ASOCIA_DERECHA = {'^', '~'} # estos operadores se agrupan de derecha a izquierda


def es_operando(caracter): # Busca o define los operandos en la expresión
    # antes era caracter.isalnum(), pero fallaba con '_'  y con decimales 
    return re.fullmatch(r"\d+\.\d+|[a-zA-Z0-9_]+", caracter) is not None # acepta letras, números, '_' y decimales


def validar_y_tokenizar(expresion): # separa en tokens, revisa que la expresión esté bien escrita y marca el menos unario
    if re.search(r"[\w.]\s+[\w.]", expresion): # detecta dos operandos separados por espacio ("a b")
        raise ValueError("Falta un operador entre dos operandos")
    expresion = expresion.replace(" ", "") # Se eliminan los espacios
    if not expresion:
        raise ValueError("La expresión está vacía")

    tokens_crudos = re.findall(r"\d+\.\d+|[a-zA-Z0-9_]+|[\+\-\*/\(\)\^]", expresion) # ahora también reconoce decimales
    if "".join(tokens_crudos) != expresion: # si al unir los tokens falta algo, había caracteres no permitidos
        raise ValueError("La expresión contiene caracteres no válidos")

    tokens = []
    esperando_operando = True # indica si lo que sigue debe ser un operando, '(' o un menos unario
    abiertos = 0 #cuenta los paréntesis abiertos para validar que estén balanceados

    for token in tokens_crudos:
        if es_operando(token):
            if not esperando_operando:
                raise ValueError("Falta un operador antes de '" + token + "'")
            tokens.append(token)
            esperando_operando = False
        elif token == "(":
            if not esperando_operando:
                raise ValueError("Falta un operador antes de '('")
            abiertos += 1
            tokens.append(token)
        elif token == ")":
            if esperando_operando:
                raise ValueError("Falta un operando antes de ')'")
            abiertos -= 1
            if abiertos < 0:
                raise ValueError("Paréntesis de cierre sin su paréntesis de apertura")
            tokens.append(token)
        else: # es un operador
            if esperando_operando:
                if token == "-": # menos unario
                    tokens.append("~")
                elif token == "+": # más unario, no cambia nada, se ignora
                    pass
                else:
                    raise ValueError("Falta un operando antes de '" + token + "'")
            else:
                tokens.append(token)
                esperando_operando = True

    if esperando_operando:
        raise ValueError("La expresión está incompleta (falta un operando al final)")
    if abiertos > 0:
        raise ValueError("Falta cerrar un paréntesis")
    return tokens


def infix_to_postfix(expresion): #Se pasa la operación infija a posfija
    #arrays
    pila = [] #pila de operadoes
    polaca = [] # Para guardar la polaca inversa

    tokens = validar_y_tokenizar(expresion) 

    for token in tokens: #Se leen los tokens y dividen si se detecta un operando va directamente al array de polaca, de lo contrario se reune en la pila
        if es_operando(token):
            polaca.append(token)
        elif token == "(": # Si el token es un parentesis abierto lo coloca en la pila de operadores
            pila.append(token)
        elif token == ")": #si en los tokens hay parentesis cerrado
            while pila and pila[-1] != "(": # Confirma que la pila no esta vacia y que el último elemento no sea (
                polaca.append(pila.pop()) # Manda el ultimo operador a polaca eliminandolo del array pila
            if pila and pila[-1] == "(": #comprueba que en la pila haya un (
                pila.pop() # Si hay lo elimina
        elif token == "~": # el menos unario es prefijo, solo se mete a la pila sin sacar nada
            pila.append(token)
        else:
            while ( # Mientras haya tokens en el array y no sean ()
                pila
                and pila[-1] != "("
                # NUEVO: si el operador es de asociación derecha (^) solo se saca si el de la pila tiene MAYOR prioridad
                and (PRECEDENCE.get(pila[-1], 0) > PRECEDENCE.get(token, 0)
                     or (PRECEDENCE.get(pila[-1], 0) == PRECEDENCE.get(token, 0) and token not in ASOCIA_DERECHA))
            ):
                polaca.append(pila.pop()) # si tiene mayor o igual prioridad se saca y manda a polaca
            pila.append(token) # Despues de comparar con los otros operadores se ingresa el actual en la pila
    #cuando ya se recorrio todos los tokens
    while pila: # se vacia la pila
        polaca.append(pila.pop()) # ingresando uno por uno en el array polaca.

    return polaca # regresa el array polaca

#Genera tres direcciones y cuádrupas
def generar_representaciones_intermedias(postfix_tokens):
    # Se definen los arrays para guardar los resultados
    pila = []  # guarda operandos y resultados temporales
    tres_direcciones = [] # guarda las tres direcciones
    cuadrupletas = [] # guarda las cuádruplas
    contador_temporales = 1 # contador de temporales t1

    for token in postfix_tokens: # recorre la expresión polaca (posfija)
        if es_operando(token): # si es un operando lo guarda directo en la pila
            pila.append(token)
        elif token == "~": # menos unario, solo usa UN operando
            op1 = pila.pop()
            temp = f"T{contador_temporales}"
            contador_temporales += 1
            tres_direcciones.append(f"{temp} = -{op1}") 
            cuadrupletas.append((token, op1, "-", temp)) # el campo vacío se muestra con "-"
            pila.append(temp)
        else: # si es un operador se optienen los dos últimos operandos de la pila
            op2 = pila.pop()
            op1 = pila.pop()

            temp = f"T{contador_temporales}" # se crea la temporal que guarda la expresión
            contador_temporales += 1 # se aumenta el contador

            instruccion_c3d = f"{temp} = {op1} {token} {op2}" # Se genera la expresin en tres direccines
            tres_direcciones.append(instruccion_c3d) # se ingresa al array

            cuadrupleta = (token, op1, op2, temp) # se crea la cuadrupleta
            cuadrupletas.append(cuadrupleta) # se ingresa al array

            pila.append(temp)  #Se guarda el temporal para volver a utilizarse

    return tres_direcciones, cuadrupletas #regresa los arrays de las tres direcciones y las cuádrupletas.


def procesar_expresion(expresion): # Función para obtener la expresión y ejecutar los resultados

    print(f"EXPRESIÓN DE ENTRADA: {expresion}")
    print("-" * 20)
    # se obtiene la expresión y se ejecuta la función para obtener la pila ploaca inversa
    try: # si la expresión está mal escrita se muestra el error en lugar de cerrar el programa
        postfix_tokens = infix_to_postfix(expresion)
    except ValueError as error:
        print(f"\nError: {error}")
        print("-" * 20 + "\n")
        return
    polaca_inversa_str = "".join(postfix_tokens) #une los elementos de la lista
    print("\na) Polaca Inversa:")
    print(f"   {polaca_inversa_str}") # imprime la polaca inversa

    # Se da a la función la pila para generar las tres direcciones y las cuadruplas
    tres_dir, cuadrupletas = generar_representaciones_intermedias(
        postfix_tokens
    )
    # Se imprimen las linas del array
    print("\nb) Tres Direcciones:")
    for linea in tres_dir:
        print(f"   {linea}")
    #Se separan e imprimen en los parentesís
    print("\nc) Cuadrupletas:")
    for op, arg1, arg2, res in cuadrupletas:
        print(f"   ({op}, {arg1}, {arg2}, {res})")

    print("-" * 20 + "\n")

# Se ejecuata el ejemplo y se establecio un while para que siga repitiendo hasta que el usuario quiera salir
if __name__ == "__main__":
    ejemplo = "a+b*c+d"
    procesar_expresion(ejemplo)

    while True:
        expresion = input("Ingresa una expresión (o 'salir' para terminar): ")
        if expresion.lower() == "salir": #Sin importar como se escriba la instrucción la convierte en minusculas
            break
        if expresion.strip():
            procesar_expresion(expresion)