import re #Se importa la libreria del regex
import os # NUEVO: sirve para revisar si existe el archivo factorial.code
import sys # NUEVO: sirve para recibir el nombre del archivo del algoritmo desde la CMD

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
def generar_representaciones_intermedias(postfix_tokens, contador_inicial=1): # NUEVO: contador_inicial permite continuar la numeración de temporales (T1, T2...) entre varias líneas del algoritmo
    # Se definen los arrays para guardar los resultados
    pila = []  # guarda operandos y resultados temporales
    tres_direcciones = [] # guarda las tres direcciones
    cuadrupletas = [] # guarda las cuádruplas
    contador_temporales = contador_inicial # contador de temporales t1

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
# algoritmo del factorial (el de la imagen); si no existe factorial.code se crea con este texto
FACTORIAL_CODE = """def factorial(n):
    if n==0 or n==1:
        resultado=1
    elif n>1:
        resultado=n*factorial(n-1)
    return resultado

fact5=factorial(5)
print(fact5)
"""

numero = {"T": 1, "L": 1} # lleva la cuenta del siguiente temporal (T1, T2...) y de la siguiente etiqueta (L1, L2...)
registro = {"polaca": []} # aquí se guarda la polaca inversa de cada expresión que se encuentra en el algoritmo


def nueva_etiqueta(): # crea L1, L2, L3...
    etiqueta = f"L{numero['L']}"
    numero["L"] += 1
    return etiqueta


def generar_llamada(nombre, argumentos, codigo, devuelve_valor): # genera los param y el call de una función
    lugares = [expresion_a_tres(arg, codigo) for arg in argumentos if arg.strip()] # cada argumento puede ser otra expresión
    for lugar in lugares:
        codigo.append(f"param {lugar}")
    llamada = f"call {nombre}, {len(lugares)}"
    if not devuelve_valor: # por ejemplo print(), no guarda resultado
        codigo.append(llamada)
        return None
    temp = f"T{numero['T']}"
    numero["T"] += 1
    codigo.append(f"{temp} = {llamada}")
    return temp


def expresion_a_tres(expresion, codigo): # convierte una expresión a tres direcciones y regresa dónde quedó el resultado
    expresion = expresion.strip()
    while True: # primero se resuelven las llamadas a funciones, de adentro hacia afuera
        llamada = re.search(r"([a-zA-Z_]\w*)\(([^()]*)\)", expresion)
        if not llamada:
            break
        temp = generar_llamada(llamada.group(1), llamada.group(2).split(","), codigo, True)
        expresion = expresion[:llamada.start()] + temp + expresion[llamada.end():] # la llamada se cambia por su temporal
    if es_operando(expresion): # si ya es un solo operando no hay nada que calcular
        return expresion
    postfix_tokens = infix_to_postfix(expresion) # se reutiliza el código de la práctica
    registro["polaca"].append(f"{expresion}   →   {' '.join(postfix_tokens)}") # se guarda su polaca inversa
    lineas_tres, _ = generar_representaciones_intermedias(postfix_tokens, numero["T"])
    numero["T"] += len(lineas_tres) # cada instrucción usa un temporal
    codigo.extend(lineas_tres)
    return f"T{numero['T'] - 1}" # el último temporal tiene el resultado final


def separar_comparacion(texto): # separa 'a >= b' en (a, >=, b)
    m = re.fullmatch(r"(.+?)\s*(==|!=|<=|>=|<|>)\s*(.+)", texto.strip())
    if not m:
        raise ValueError(f"Condición no válida: '{texto.strip()}'")
    return m.group(1), m.group(2), m.group(3)


def comparar(parte, codigo): # resuelve los dos lados de una comparación, guarda su polaca y regresa "izq op der"
    izq, op, der = separar_comparacion(parte)
    lugar_izq = expresion_a_tres(izq, codigo)
    lugar_der = expresion_a_tres(der, codigo)
    registro["polaca"].append(f"{parte.strip()}   →   {lugar_izq} {lugar_der} {op}")
    return f"{lugar_izq} {op} {lugar_der}"


def condicion_a_tres(condicion, etiqueta_si, codigo): # genera los saltos de una condición (soporta 'or' y 'and')
    if " and " in condicion: # and: si alguna parte falla se salta, si todas pasan se va al cuerpo
        etiqueta_no = nueva_etiqueta()
        for parte in condicion.split(" and "):
            codigo.append(f"ifFalse {comparar(parte, codigo)} goto {etiqueta_no}")
        codigo.append(f"goto {etiqueta_si}")
        codigo.append(f"{etiqueta_no}:")
        return
    for parte in condicion.split(" or "): # or: si alguna parte se cumple se va al cuerpo
        codigo.append(f"if {comparar(parte, codigo)} goto {etiqueta_si}")


def traducir_cuerpo(lineas, i, codigo): # traduce el cuerpo que empieza en la línea i (todas las líneas con esa misma sangría)
    return traducir_bloque(lineas, i, lineas[i][0], codigo)


def traducir_bloque(lineas, i, nivel, codigo): # recorre las líneas del algoritmo según su sangría (indentación)
    while i < len(lineas) and lineas[i][0] >= nivel:
        sangria, texto = lineas[i]

        if texto.startswith("def "): # definición de función
            m = re.fullmatch(r"def\s+(\w+)\((.*)\):", texto)
            codigo.append(f"func {m.group(1)}({m.group(2).strip()})")
            i = traducir_cuerpo(lineas, i + 1, codigo)
            codigo.append("endfunc")

        elif texto.startswith("if "): # if / elif / else
            ramas = [] # cada rama es (condición, código de su cuerpo)
            sino = [] # código del else
            cuerpo = []
            i = traducir_cuerpo(lineas, i + 1, cuerpo)
            ramas.append((texto[3:].rstrip(":").strip(), cuerpo))
            while i < len(lineas) and lineas[i][0] == sangria and lineas[i][1].startswith(("elif ", "else:")):
                if lineas[i][1].startswith("elif "):
                    cuerpo = []
                    condicion = lineas[i][1][5:].rstrip(":").strip()
                    i = traducir_cuerpo(lineas, i + 1, cuerpo)
                    ramas.append((condicion, cuerpo))
                else:
                    i = traducir_cuerpo(lineas, i + 1, sino)
            etiquetas = [nueva_etiqueta() for _ in ramas]
            etiqueta_sino = nueva_etiqueta()
            etiqueta_fin = nueva_etiqueta()
            for (condicion, _), etiqueta in zip(ramas, etiquetas): # primero se evalúan todas las condiciones
                condicion_a_tres(condicion, etiqueta, codigo)
            codigo.append(f"goto {etiqueta_sino}")
            for (_, cuerpo), etiqueta in zip(ramas, etiquetas): # después van los cuerpos
                codigo.append(f"{etiqueta}:")
                codigo.extend(cuerpo)
                codigo.append(f"goto {etiqueta_fin}")
            codigo.append(f"{etiqueta_sino}:")
            codigo.extend(sino)
            codigo.append(f"{etiqueta_fin}:")

        elif texto.startswith("while "): # ciclo while
            condicion = texto[6:].rstrip(":").strip()
            cuerpo = []
            i = traducir_cuerpo(lineas, i + 1, cuerpo)
            inicio, dentro, fin = nueva_etiqueta(), nueva_etiqueta(), nueva_etiqueta()
            codigo.append(f"{inicio}:")
            condicion_a_tres(condicion, dentro, codigo)
            codigo.append(f"goto {fin}")
            codigo.append(f"{dentro}:")
            codigo.extend(cuerpo)
            codigo.append(f"goto {inicio}")
            codigo.append(f"{fin}:")

        elif texto == "return" or texto.startswith("return "): # return
            valor = texto[6:].strip()
            codigo.append(f"return {expresion_a_tres(valor, codigo)}" if valor else "return")
            i += 1

        elif re.fullmatch(r"[a-zA-Z_]\w*\(.*\)", texto): # llamada sola, por ejemplo print(fact5)
            m = re.fullmatch(r"([a-zA-Z_]\w*)\((.*)\)", texto)
            generar_llamada(m.group(1), m.group(2).split(","), codigo, False)
            i += 1

        else: # asignación: variable = expresión
            m = re.fullmatch(r"([a-zA-Z_]\w*)\s*=\s*(.+)", texto)
            if not m:
                raise ValueError(f"Instrucción no reconocida: '{texto}'")
            codigo.append(f"{m.group(1)} = {expresion_a_tres(m.group(2), codigo)}")
            i += 1
    return i


def dar_formato(codigo): # acomoda la sangría final: etiquetas y func/endfunc a la izquierda, lo de dentro de la función con 4 espacios
    final = []
    en_funcion = False
    for linea in codigo:
        if linea.startswith("func "):
            en_funcion = True
            final.append(linea)
        elif linea == "endfunc":
            en_funcion = False
            final.append(linea)
        elif linea.endswith(":"): # las etiquetas (L1:) siempre van a la izquierda
            final.append(linea)
        elif en_funcion:
            final.append("    " + linea)
        else:
            final.append(linea)
    return final


def algoritmo_a_tres(fuente): # lee el algoritmo completo y regresa las líneas en tres direcciones
    numero["T"] = 1 # se reinician los contadores
    numero["L"] = 1
    registro["polaca"] = []
    lineas = [] # cada línea se guarda como (sangría, texto)
    for linea in fuente.splitlines():
        linea = linea.replace("\t", "    ").rstrip()
        linea = re.sub(r"^\s*>>>\s?", "", linea) # por si se copió con el prompt de Python
        if not linea.strip() or linea.strip().startswith("#"): # se ignoran líneas vacías y comentarios
            continue
        lineas.append((len(linea) - len(linea.lstrip()), linea.strip()))
    codigo = []
    traducir_bloque(lineas, 0, 0, codigo)
    return dar_formato(codigo)


def tres_a_cuadruplas(tres_dir): # convierte cada línea de tres direcciones en su cuádrupla (operador, arg1, arg2, resultado)
    cuadruplas = []
    for linea in tres_dir:
        linea = linea.strip()
        asignacion = re.fullmatch(r"(\w+) = (.+)", linea)
        if linea.endswith(":"): # etiqueta
            cuadruplas.append(("label", "-", "-", linea[:-1]))
        elif asignacion: # T1 = b * c, T1 = -a, x = T1, T2 = call f, 1
            destino, resto = asignacion.groups()
            llamada = re.fullmatch(r"call (\w+), (\d+)", resto)
            partes = resto.split()
            if llamada:
                cuadruplas.append(("call", llamada.group(1), llamada.group(2), destino))
            elif len(partes) == 3: # operación binaria
                cuadruplas.append((partes[1], partes[0], partes[2], destino))
            elif resto.startswith("-"): # menos unario
                cuadruplas.append(("~", resto[1:], "-", destino))
            else: # asignación simple
                cuadruplas.append(("=", resto, "-", destino))
        elif linea.startswith("func "):
            m = re.fullmatch(r"func (\w+)\((.*)\)", linea)
            cuadruplas.append(("func", m.group(1), m.group(2) or "-", "-"))
        elif linea == "endfunc":
            cuadruplas.append(("endfunc", "-", "-", "-"))
        elif linea.startswith("goto "):
            cuadruplas.append(("goto", "-", "-", linea[5:]))
        elif linea.startswith(("if ", "ifFalse ")):
            m = re.fullmatch(r"(if|ifFalse) (.+) (==|!=|<=|>=|<|>) (.+) goto (\w+)", linea)
            cuadruplas.append((m.group(1) + m.group(3), m.group(2), m.group(4), m.group(5)))
        elif linea.startswith("param "):
            cuadruplas.append(("param", linea[6:], "-", "-"))
        elif linea == "return" or linea.startswith("return "):
            cuadruplas.append(("return", linea[6:].strip() or "-", "-", "-"))
        else: # llamada sin resultado: call print, 1
            m = re.fullmatch(r"call (\w+), (\d+)", linea)
            cuadruplas.append(("call", m.group(1), m.group(2), "-"))
    return cuadruplas


def procesar_algoritmo(archivo_entrada="factorial.code", archivo_salida="factorial.txt"): #lee el algoritmo, muestra sus tres formas y guarda las tres direcciones en un .txt
    if not os.path.exists(archivo_entrada) and archivo_entrada == "factorial.code": # si no existe factorial.code se crea con el algoritmo del factorial
        with open(archivo_entrada, "w", encoding="utf-8") as f:
            f.write(FACTORIAL_CODE)
    try:
        with open(archivo_entrada, encoding="utf-8") as f:
            fuente = f.read()
    except FileNotFoundError:
        print(f"No se encontró el archivo: {archivo_entrada}")
        return
    print(f"ALGORITMO DE ENTRADA ({archivo_entrada}):")
    print("-" * 20)
    print(fuente)
    print("-" * 20)
    try:
        tres_dir = algoritmo_a_tres(fuente)
        cuadruplas = tres_a_cuadruplas(tres_dir)
    except (ValueError, IndexError, AttributeError) as error:
        print(f"\nError: {error}")
        return
    print("\na) Polaca Inversa (de cada expresión):")
    for linea in registro["polaca"]:
        print(f"   {linea}")
    print("\nb) Tres Direcciones:")
    for linea in tres_dir:
        print(f"   {linea}")
    print("\nc) Cuadrupletas:")
    for op, arg1, arg2, res in cuadruplas:
        print(f"   ({op}, {arg1}, {arg2}, {res})")
    with open(archivo_salida, "w", encoding="utf-8") as f: # se guardan las tres direcciones en el .txt
        f.write("\n".join(tres_dir) + "\n")
    print("-" * 20)
    print(f"Archivo guardado: {archivo_salida}\n")

# Se ejecuata el ejemplo y se establecio un while para que siga repitiendo hasta que el usuario quiera salir
if __name__ == "__main__":
    archivo = sys.argv[1] if len(sys.argv) > 1 else "factorial.code" # se puede indicar otro algoritmo: python compilador_intermedio.py otro.code
    procesar_algoritmo(archivo, os.path.splitext(archivo)[0] + ".txt") # traduce el algoritmo de forma automática y genera su .txt

    while True:
        expresion = input("Ingresa una expresión (o 'salir' para terminar): ")
        if expresion.lower() == "salir": #Sin importar como se escriba la instrucción la convierte en minusculas
            break
        if expresion.strip():
            procesar_expresion(expresion)