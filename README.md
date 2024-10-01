# Python DNS Proxy Server

## Modo de uso:
El script tomará los argumentos que el usuario le pase por consola si es que no existe un archivo de configuración próximo al script. Si el usuario no introduce algún argumento, se tomará el valor por defecto de ese parámetro. Si el archivo de configuración existe, se tomarán los valores del mismo ignorando así los argumentos pasados por la línea de comandos, a menos que se especifique la flag --use-args, la cual forzará al script a usar los argumentos pasados por consola. El archivo de configuración se puede crear al introducir el parámetro --save-config, el cual guardará en el archivo todos los valores pasados como argumento. Cada parámetro tomará su valor por defecto si es que el usuario no introduce el argumento.

La sección [MAP] del archivo de configuración será utilizada para asignarle una IP a un dominio de forma manual. Cada vez que se pregunte por ese dominio, se responderá con la IP que se le asigne.

La sección [EXCEPTIONS] del archivo de configuración será utilizada para verificar si la IP desde donde se hace la petición coincide con la IP a la que está mapeado el dominio por el que se pregunta. Si es así, se forzará al servidor DNS proxy local a hacerle una petición al servidor DNS remoto por ese dominio, incluso si ese dominio está manualmente mapeado una dirección IP en la sección [MAP]. Si otro IP pregunta por ese dominio, se le responderá de acuerdo al contenido de la sección [MAP].

Para ambas secciones: Si en el lugar del dominio, aparece una palabra, por ejemplo, ip, precedido por el carácter $, no se tomará en cuenta ese dominio. Esto es, por ejemplo, para poder crear una variable y asignarla a un dominio de la siguiente forma: dominio = %($ip)s. Esta variable será local en cada sección, es decir, la variable $ip en la sección [MAP] no existirá en la sección [EXCEPTIONS]. Para que una variable sea accesible desde todas las secciones, debe definirse en la sección [DEFAULT].

## Parámetros:

- port : Puerto local por el cual el servidor estará a la escucha. Por defecto 53.

- -a, --address \<address> : Interfaz por la cual actuará el servidor. Por defecto todas las interfaces.

- -u, --upstream \<address>:\<port> : Servidor DNS de destino. Por defecto 1.1.1.1 por el puerto 53.

- -t, --timeout : Tiempo máximo a esperar por la respuesta del servidor de destino. Por defecto 5 segundos. Si pasa ese tiempo, el servidor proxy enviará la respuesta NXDOMAIN (Non-Existent Domain).

- --log \<log_format>: Formato de salida en consola de las peticiones y respuestas hechas por el servidor.

- --log-prefix : Si incluir en los logs la hora del evento y otros metadatos.

- --save-config [config_file_path] : Archivo en el cual guardar los valores de los argumentos pasados al script (excepto --save-config y --use-args). Se comportará de la siguiente manera:
    1. No se especifica la flag ni su argumento: No se guardará la configuración en un archivo.
    2. Se especifica la flag pero no su argumento: Se guardará la configuración en un archivo con nombre por defecto `dns_proxy_settings.ini`.
    3. Se especifica la flag con su argumento: Se usará ese nombre de archivo como el nombre del archivo de configuración.

- --use-args : Actúa como flag. Si se especifica, se usarán los argumentos introducidos por consola y se ignorarán los valores contenidos en el archivo de configuración. Por defecto se utiliza el archivo de configuración al leer los valores.

- -m, --map \<dominio:ip> : Si se especifica, debe pasarse como argumento almenos un par \<dominio:ip>. Si se pasarán mas de un par, deben ir separados o por comas, o por espacios.

- -x, --exceptions \<dominio:ip> : El paso de argumentos es igual al del parámetro --map.

### Ejemplo de archivo de configuración .ini
```ini
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

## Ejemplo de funcionamiento (tomando en cuenta la configuración anterior):
```
IP <192.168.1.10> pregunta por el dominio <personal.domain1>
DNSProxy responde a <192.168.1.10>: <personal.domain1> está en <192.168.1.10>

IP <192.168.1.12> pregunta por el dominio <personal.domain5>
DNSProxy pregunta a servidor remoto <8.8.8.8> por el dominio <personal.domain5>
DNSProxy responde a <192.168.1.12> con la respuesta del servidor remoto <8.8.8.8>

IP <192.168.42.85> pregunta por el dominio <www.personal.domain3>
DNSProxy responde a <192.168.42.85>: <www.personal.domain3> está en <192.168.1.1>

IP <192.168.42.86> pregunta por el dominio <www.personal.domain3>
DNSProxy pregunta a servidor remoto <8.8.8.8> por el dominio <www.personal.domain3>
DNSProxy responde a <192.168.42.86> con la respuesta del servidor remoto <8.8.8.8>
```