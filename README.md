# Python DNS Proxy Server

## Modo de uso:
El script tomará los argumentos por defecto si es que no hay un archivo de configuración. Si el archivo existe, se tomará la configuración del mismo. Si se especifica el parámetro --use-args, se forzará el uso de los argumentos pasados al script por la línea de comandos. El archivo de configuración se puede crear con el parámetro --save-config, el cual guardará en el archivo todos los valores pasados como argumento. Si no se pasó algún parámetro, se tomará el que es por defecto.

El mapa indicado abajo en el archivo de configuarción de ejemplo, será utilizado para asignarle una IP a un dominio dado. Si en el lugar del dominio, aparece una palabra, por ejemplo, ip, precedido por el carácter $, no se tomará en cuenta ese dominio. Esto es para poder crear una variable y asignarla a un dominio de la siguiente forma: dominio = %($ip)s

## Parámetros:

- port : Puerto local por el cual el servidor estará a la escucha. Por defecto 53.

- -a, --address \<address> : Interfaz por la cual actuará el servidor. Por defecto todas las interfaces.

- -u, --upstream \<address>:\<port> : Servidor DNS de destino. Por defecto 1.1.1.1 por el puerto 53.

- -t, --timeout : Tiempo máximo a esperar por la respuesta del servidor de destino. Por defecto 5 segundos.

- --log \<log_format>: Formato de salida en consola de las peticiones y respuestas hechas por el servidor.

- --log-prefix : Si incluir en los logs la hora del evento y otros metadatos.

- --save-config [config_file_path] : Si se especifica, se guardarán todos los argumentos introducidos por consola en un archivo de configuración. De otra manera, no se guarda ninguna configuración. Si no se especifica un argumento, se toma por defecto el archivo dns_proxy_settings.ini

- --use-args : Si se especifica, se usarán los argumentos introducidos por consola y se ignorará el archivo de configuración. Por defecto se utiliza el archivo de configuración.

- -m, --map \<dominio:ip> : Si se especifica, debe pasarse almenos un par dominio:ip. Cuando se haga una petición por el dominio dado, se responderá con la ip dada.

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
```