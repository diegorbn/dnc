# Integrantes
1. Diego Jose Urbina Reyes (00544424)
2. Kevin Isaac Perez Obando (00544024)
3. Luis Guillermo Orozco Lazo (00588124)
4. Daniel Alejandro Melendez Delgado (00078623)

# Definitely Not C (DNC)

**Definitely Not C (DNC)** es un proyecto educativo desarrollado en Python que implementa un analizador para un subconjunto del lenguaje C.

El proyecto comprende tres etapas:

- **Análisis léxico:** reconoce los elementos del código y los convierte en tokens.
- **Análisis sintáctico:** verifica la estructura del programa mediante un parser descendente recursivo y construye un árbol de sintaxis abstracta (AST).
- **Análisis semántico:** comprueba declaraciones de variables, ámbitos (scopes) y compatibilidad de tipos.

La gramática del lenguaje se encuentra en [docs/dnc_ebnf.txt](docs/dnc_ebnf.txt).

DNC actualmente analiza y valida programas, pero no los ejecuta ni genera código ensamblador.

## 1. Requisitos

- Python 3.
- Una terminal (Ubuntu, PowerShell o CMD).
- El código fuente del proyecto.

No es necesario utilizar un IDE.

Todos los comandos deben ejecutarse desde la **carpeta raíz del proyecto**, donde se encuentra `dnc.py`.

## 2. Ejecución en Ubuntu

Abrir una terminal en la carpeta del proyecto.

Para verificar que Python está instalado:

```bash
python3 --version
```

### Análisis léxico

```bash
python3 -m demo.lexer_demo demo/samples/valid.dnc
```

Muestra los tokens reconocidos, sus tipos, lexemas, posiciones y el total de tokens, incluyendo EOF.

### Análisis semántico

```bash
python3 -m demo.semantic_demo demo/samples/valid.dnc
```

Procesa el programa y muestra las tablas de símbolos de los diferentes ámbitos, incluyendo los nombres y tipos de las variables.

### Ejemplos con errores

Error léxico:

```bash
python3 -m demo.lexer_demo demo/samples/lexical_error.dnc
```

Error semántico:

```bash
python3 -m demo.semantic_demo demo/samples/semantic_error.dnc
```

Estos ejemplos permiten observar cómo el analizador identifica y reporta los errores.

## 3. Ejecución en Windows

Abrir PowerShell o CMD en la carpeta raíz del proyecto.

Verificar que Python está instalado:

```powershell
py -3 --version
```

### Análisis léxico

```powershell
py -3 -m demo.lexer_demo demo/samples/valid.dnc
```

### Análisis semántico

```powershell
py -3 -m demo.semantic_demo demo/samples/valid.dnc
```

### Ejemplos con errores

Error léxico:

```powershell
py -3 -m demo.lexer_demo demo/samples/lexical_error.dnc
```

Error semántico:

```powershell
py -3 -m demo.semantic_demo demo/samples/semantic_error.dnc
```

**Nota:** Si `py -3` no está disponible, se puede intentar con `python`, siempre que Python esté instalado y configurado en el PATH.

## 4. Uso del analizador principal

Además de las demostraciones, es posible analizar directamente un archivo `.dnc`.

En Ubuntu:

```bash
python3 dnc.py demo/samples/valid.dnc
```

En Windows:

```powershell
py -3 dnc.py demo/samples/valid.dnc
```

Este comando realiza el análisis léxico y muestra los tokens encontrados.

Para realizar el análisis completo, incluyendo la verificación sintáctica y semántica, utilizar la opción `--check`.

Ubuntu:

```bash
python3 dnc.py --check demo/samples/valid.dnc
```

Windows:

```powershell
py -3 dnc.py --check demo/samples/valid.dnc
```

Si el programa es válido, finaliza con código de salida `0`. Si encuentra errores, los reporta por la salida de error estándar y finaliza con código `1`.

La instrucción `print` de DNC se reconoce y valida, pero no imprime resultados calculados, ya que el proyecto no ejecuta los programas analizados.

## 5. Funcionamiento del analizador

### Lexer

Recorre el código fuente y genera tokens con su tipo, lexema, línea y columna. También detecta caracteres no reconocidos.

### Parser

Recibe la lista de tokens y utiliza funciones basadas en las producciones de la gramática EBNF para verificar que el programa tenga una estructura válida.

Si el análisis es correcto, construye un AST. Si encuentra un error sintáctico, lo reporta con su ubicación.

### Analizador semántico

Recorre el AST y verifica:

- Que las variables utilizadas hayan sido declaradas y sean accesibles desde su ámbito.
- Que no existan declaraciones duplicadas dentro del mismo ámbito.
- Que las asignaciones y operaciones respeten los tipos de datos.
- Que las condiciones y los operadores reciban los tipos correspondientes.

Los bloques anidados pueden declarar variables con nombres existentes en ámbitos exteriores. Para resolver un identificador, el analizador busca desde el ámbito más interno hacia los exteriores.

DNC admite `int` y `bool`, sin conversiones implícitas entre estos tipos. No implementa comprobaciones de inicialización definitiva.

El algoritmo del análisis semántico se documenta en [SEMANTIC_ANALYZER_ALGORITHM.md](tasks/semantic/SEMANTIC_ANALYZER_ALGORITHM.md).

## 6. Pruebas automatizadas

Para ejecutar las pruebas del proyecto:

**Ubuntu:**

```bash
python3 -m unittest discover -s tests
```

**Windows:**

```powershell
py -3 -m unittest discover -s tests
```

Estas pruebas permiten verificar el comportamiento de los componentes implementados.

## 7. Reflexión: límites de una gramática libre de contexto (CFG)

Una gramática libre de contexto (CFG) permite definir la estructura sintáctica de un lenguaje. Por ejemplo, puede establecer cómo se escribe una declaración, una asignación o un bloque de instrucciones.

Sin embargo, existen verificaciones semánticas que no pueden expresarse de manera general mediante una CFG por sí sola.

Un ejemplo es la regla **«toda variable utilizada debe haber sido declarada previamente»**. Para comprobarla, no basta con reconocer que una instrucción contiene un identificador: también debemos recordar qué variables se declararon y determinar si son accesibles desde el ámbito donde se utilizan.

Lo mismo sucede con la detección de declaraciones duplicadas y la comprobación de tipos. Estas verificaciones requieren conservar y consultar información obtenida durante el análisis del programa.

Esto se relaciona con los **lenguajes sensibles al contexto**, que permiten expresar restricciones donde la validez de ciertos elementos depende del contexto que los rodea. Por ejemplo, comprobar la correspondencia entre nombres de identificadores arbitrarios exige relaciones que una CFG no puede imponer de forma general.

En DNC resolvemos estas limitaciones separando el análisis sintáctico del semántico. El Parser construye el AST siguiendo nuestra CFG, mientras que el analizador semántico utiliza tablas de símbolos y ámbitos para realizar las verificaciones adicionales.

Por tanto, **un programa puede cumplir todas las reglas sintácticas y aun así ser semánticamente incorrecto**. Esta es una de las principales conclusiones del proyecto.