# Python DNS Proxy Server

## Modo de uso:
El script tomará los argumentos que el usuario le pase por consola si es que no existe un archivo de configuración próximo al script. Si el usuario no introduce algún argumento, se tomará el valor por defecto de ese parámetro. Si el archivo de configuración existe, se tomarán los valores del mismo ignorando así los argumentos pasados por la línea de comandos, a menos que se especifique la flag --use-args, la cual forzará al script a usar los argumentos pasados por consola. El archivo de configuración se puede crear al introducir el parámetro --save-config, el cual guardará en el archivo todos los valores pasados como argumento. Cada parámetro tomará su valor por defecto si es que el usuario no introduce el argumento.

El mapa indicado abajo en el archivo de configuración de ejemplo, será utilizado para asignarle una IP a un dominio dado. Si en el lugar del dominio, aparece una palabra, por ejemplo, ip, precedido por el carácter $, no se tomará en cuenta ese dominio. Esto es, por ejemplo, para poder crear una variable y asignarla a un dominio de la siguiente forma: dominio = %($ip)s

La sección [EXCEPTIONS] del archivo de configuración será utilizada para verificar si la IP desde donde se hace la petición coincide con la IP a la que está mapeado el dominio por el que se pregunta. Si es así, se forzará al servidor DNS proxy local a hacerle una petición al servidor DNS remoto por ese dominio, incluso si ese dominio está manualmente mapeado a esa misma dirección IP en la sección [MAP]. Si otro IP pregunta por ese dominio, se le responderá de acuerdo al contenido de la sección [MAP]. El funcionamiento del carácter $ es igual que el de la sección [MAP]

## Parámetros:

- port : Puerto local por el cual el servidor estará a la escucha. Por defecto 53.

- -a, --address \<address> : Interfaz por la cual actuará el servidor. Por defecto todas las interfaces.

- -u, --upstream \<address>:\<port> : Servidor DNS de destino. Por defecto 1.1.1.1 por el puerto 53.

- -t, --timeout : Tiempo máximo a esperar por la respuesta del servidor de destino. Por defecto 5 segundos. Si pasa ese tiempo, el servidor proxy enviará la respuesta NXDOMAIN (Non-Existent Domain).

- --log \<log_format>: Formato de salida en consola de las peticiones y respuestas hechas por el servidor.

- --log-prefix : Si incluir en los logs la hora del evento y otros metadatos.

- --save-config [config_file_path] : Si se especifica, se guardarán todos los argumentos introducidos por consola (excepto --save-config y --use-args) en un archivo de configuración con nombre por defecto. Si no se especifica un argumento, se toma por defecto el archivo dns_proxy_settings.ini

- --use-args : Actúa como flag. Si se especifica, se usarán los argumentos introducidos por consola y se ignorarán los valores contenidos en el archivo de configuración. Por defecto se utiliza el archivo de configuración al leer los valores.

- -m, --map \<dominio:ip> : Si se especifica, debe pasarse como argumento almenos un par \<dominio:ip>. Si se pasarán mas de un par, deben ir separados o por comas, o por espacios. Cuando se haga una petición por el/los dominio/s dado/s, se responderá con la ip dada.

- -x, --exceptions \<dominio:ip> : El paso de argumentos es igual al del parámetro --map. Cuando se haga una petición por el/los dominio/s dado/s, se verificará si el cliente que hace la petición coincide con el valor de la IP a la que está asignado el dominio de la petición. Si es así, obligará al servidor proxy local a hacer una petición por ese dominio al servidor DNS base, incluso si está manualmente asignado a esa misma IP en el archivo de configuración.

### Ejemplo de archivo de configuración .ini
```
[DEFAULT]
address = 0.0.0.0
port = 53
upstream = 1.1.1.1:53
timeout = 5
log = request,reply,truncated,error
log_prefix = False

[SAVED]
address = 192.168.1.2
upstream = 8.8.8.8:53

[MAP]
$ip = 192.168.1.10
personal.domain1 = %($ip)s
personal.domain2 = 192.168.42.86
www.personal.domain3 = 192.168.1.1

[EXCEPTIONS]
www.personal.domain3 = 192.168.42.86
```

## Ejemplo de utilización:
```
Usuario con IP 192.168.1.10 pregunta por el dominio personal.domain1
Servidor local responde a 192.168.1.10: personal.domain1 está en 192.168.1.10

Usuario con IP 192.168.1.12 pregunta por el dominio personal.domain5
Servidor local pregunta a servidor remoto por el dominio personal.domain5
Servidor local responde a 192.168.1.12 con la respuesta del servidor remoto

Usuario con IP 192.168.42.85 pregunta por el dominio www.personal.domain3
Servidor local responde a 192.168.42.85: www.personal.domain3 está en 192.168.1.1

Usuario con IP 192.168.42.86 pregunta por el dominio www.personal.domain3
Servidor local pregunta a servidor remoto por el dominio www.personal.domain3
Servidor local responde a 192.168.42.86 con la respuesta del servidor remoto
```