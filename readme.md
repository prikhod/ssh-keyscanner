usage: ```python -m ssh_keyscanner [-h] -c CONFIG (-f FILE | (-a HOST -p PORT))```

usage: ```python -m search_duplicates [-h] -c CONFIG```

usage: ```python -m notification [-h] -c CONFIG```

Для добавления новой задачи отредактируйте setup_cron.sh и start_scan.sh установив пути к исполняемым файлам.

Запустите setup_cron.sh, задача добавится в расписание.
Опции:

-с файл конфигурации, config.yaml

-f файл в формате ```host:port``` по одной записи на строку 

-h host, в формате  ```192.168.0.1``` или сеть ```192.168.0.0/24```

-p port для выбранного узла или сети

Для поиска дубликатов ключей используйте search_duplicates с конфигом config.yaml

Для запуска системы оповещения используйте notification с конфигом config-notification.yaml 


#Tests ssh-keyscan

for 87.250.0.0/22

scan complete in 20.251219987869263s

for 87.250.0.0/20

scan complete in 81.64969253540039s

for 87.250.0.0/16

scan complete in 1404.3057894706726s



# Test my ssh-keyscanner

[//]: # ()
[//]: # (for 87.250.0.0/22 | 140 workers | 2s timeout)

[//]: # ()
[//]: # (scan complete in 37.82651495933533s)

for 87.250.0.0/22 | 20 workers | 1s timeout

scan complete in 35.86569142341614s

for 87.250.0.0/20 | 50 workers | 1s timeout

scan complete in 144.6835069656372s

for 87.250.0.0/16 | 50 workers | 1s timeout

scan complete in 2653.8321922272011s

