# SEEP - Buffer

Este repositorio contiene el backend en la nube del **Sistema de Entrega de Exámenes Parciales (SEEP)**. Funciona como un servidor intermediario diseñado para eludir las restricciones físicas y lógicas de las redes de la facultad.

## Justificación de la Arquitectura (Triangulación)

En la versión original LAN de SEEP, el docente actuaba como un servidor local y los alumnos como clientes. Sin embargo, la red de la facultad presenta obstáculos para la comunicación par a par (P2P).

**La Solución:** Dado que las computadoras del laboratorio cuentan con salida a Internet, la arquitectura evoluciona hacia una triangulación en la nube. Ambos actores (Docente y Alumno) pasan a ser **clientes** de este pequeño servidor central, comunicándose a través del puerto seguro 443 (HTTPS).

> **Dato de Color:** Esta arquitectura es una implementación práctica del patrón **Productor-Consumidor** que se enseña en el módulo concurrente de _Taller de Programación_.

## Flujo de Trabajo (Productor - Consumidor)

El servidor mantiene un diccionario efímero en la memoria RAM que actúa como buzón temporal. El sistema no utiliza bases de datos persistentes.

1. **Apertura (Docente):** El Cliente Docente hace una petición POST al inicio del examen. El servidor crea un buzón vacío y devuelve un `PIN` aleatorio de 4 dígitos.
2. **Productor (Alumno):** El Cliente Alumno empaqueta su archivo `.pas` (codificado en Base64 para evitar corrupción de binarios) y hace un POST seguro al servidor junto con sus datos y el `PIN`. El servidor encola la entrega en el buzón.
3. **Consumidor (Docente):** El Cliente Docente realiza peticiones GET periódicas (_polling_ automático cada 5 segundos) consultando el buzón.
4. **Descarga y Limpieza (ACK):** Cuando hay entregas, el Docente las descarga, las decodifica, las guarda en su disco duro local y envía un POST de confirmación (ACK) al servidor. Al recibir la confirmación, **el servidor elimina el parcial de la nube**, liberando la memoria.
5. **Cierre:** Al finalizar, el consumidor envía un comando `DELETE` que destruye el buzón por completo.

## Seguridad y Concurrencia

Al estar expuesto en la Internet pública (desplegado en servicios como Render), el servidor implementa varias capas de seguridad:

- **Rate Limiting:** Bloquea peticiones masivas mediante `Flask-Limiter` para evitar ataques de denegación de servicio (DoS) y spam de entregas.
- **CORS:** Restricción de orígenes cruzados gestionada por `Flask-CORS`.
- **Limpieza de Memoria:** Almacenamiento estrictamente volátil; ningún examen sobrevive en la nube una vez que el docente confirma su recepción.

## Despliegue y Pruebas Locales

Este proyecto utiliza **Poetry** para la gestión de dependencias y está preparado para entornos de producción en Linux mediante **Gunicorn**.

**Instalación local:**

```bash
git clone [https://github.com/Erasmo-tries-to-dev/SEEP-Buffer.git](https://github.com/Erasmo-tries-to-dev/SEEP-Buffer.git)
cd SEEP-Buffer
poetry install
```
