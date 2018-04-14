docker-compose build
docker-compose up

cp hologram.nginxconf /etc/nginx/sites-enabled/hologram
sudo service nginx restart

