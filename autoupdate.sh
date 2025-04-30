#!/bin/bash
server='ip-service.net.ua'

token="SACdh!V27VxBG7@a"

api_server="http://$server/public/api.php"
backup_dir="/home/vanya/backup"
backup_file="$backup_dir/backup.tar.gz"
local_dir="/home/vanya"

# Отримання локальних IP-адрес
local_ips=$(hostname -I | tr ' ' '\n' | grep -v '127.0.0.1' | paste -sd "," -)

# Перевірка доступності сервера за допомогою curl
response=$(curl --write-out '%{http_code}' --silent --output /dev/null "$api_server")

if [ "$response" -eq 200 ]; then
    echo "# Connection success!"
    
    if nc -z $server 80 2>/dev/null; then
        echo "server online"
        
        serverdata=$(curl -X POST -F "id=$token" -F "op=check" -F "comment=$local_ips" "$api_server" 2>/dev/null)
        echo $serverdata
        
        update_request=$(echo $serverdata | awk -F ';' '{print $3}')
        
        if [[ $update_request == 1 ]]; then
            filename=$(echo $serverdata | awk -F ';' '{print $1}')
            cd $local_dir
            rm -f $local_dir/*.tar.gz
            rm -rf ~/*GUI*/

            # Спроба завантажити файл
            curl -v --user update_system:user1234 -O "$server/update_mngr/$filename"
            if [ $? -ne 0 ]; then
                echo "Failed to download $filename, using backup archive"
                tar -xf $backup_file -C $local_dir
            else
                echo "file: $server/update_mngr/$filename"
                mv "$local_dir/$filename" "$backup_file"
                tar -xf $backup_file -C $local_dir
            fi

            # Надсилання запиту завершення
            serverdata=$(curl -X POST -F "id=$token" -F "op=complete" "$api_server")
        fi
    else
        echo "server unreachable, using backup archive"
        tar -xf $backup_file -C $local_dir
    fi
else
    echo "Server is not accessible. HTTP response code: $response, using backup archive"
    tar -xf $backup_file -C $local_dir
fi
