# Demostraciones de DNC

Desde la raíz del proyecto, ejecuta:

```sh
python -m demo.lexer_demo demo/samples/valid.dnc
python -m demo.semantic_demo demo/samples/valid.dnc
```

El analizador léxico muestra los tokens, sus posiciones y el total, incluido
EOF. El analizador semántico muestra las variables y tipos de cada ámbito al
terminar su análisis; los ámbitos anidados pueden compartir el mismo nivel.

Para ver errores reales de cada etapa:

```sh
python -m demo.lexer_demo demo/samples/lexical_error.dnc
python -m demo.semantic_demo demo/samples/semantic_error.dnc
```
