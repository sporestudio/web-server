# Web server deployment

> \[!WARNING\]
> 
> This app is under development. Keep your expectations low.

Automated deployment of a web server made with Docker containers. The server is composed by a main domain with the main page of the web, and serveral subdomains used for two aplications: **an url shortener and a youtube video and audio downloader**. 
We have another two subdomain, one of these for the grafana monitoring interface and another one for the jenkins panel administration.

## Structure

```
├── web-server
│   ├── certbot
│   │   ├── htdocs
|   |   |   └── index.html
|   |   └── httpd.conf
│   ├── url-shortner
|   |   ├── static
|   |   ├── templates
|   |   ├── tests  
|   |   ├── app.py
|   |   ├── dns_manager.py
|   |   ├── Dockerfile
|   |   ├── requirements.txt
|   |   └── widgets.py
|   ├── web
|   |   ├── htdocs
|   |   |   ├── admin
|   |   |   ├── assets
|   |   |   ├── styles
|   |   |   ├── .htpasswd
|   |   |   ├── contact.html
|   |   |   ├── error404.html
|   |   |   ├── forbidden403.html
|   |   |   ├── index.html
|   |   |   └── logo.png
|   |   ├── httpd-vhosts.conf
|   |   └── httpd.conf
|   ├── web-downloader
|   |   ├── static
|   |   |   └── style.css
|   |   ├── templates
|   |   |   └── index.html
|   |   ├── app.py
|   |   ├── Dockerfile
|   |   └── requirements.txt
|   ├── autostart.sh
|   ├── config.json
|   └── config.py

```

## Dependencies

The required dependecies for deploy the project are:

- Docker
- docker-composed
- make

## Previous configurations

### Router configurations

In this project the server will be my personal computer, which does not have a public IP, so we must map port 80 of our router with port 8080 of our machine, as well as port 443 with port 4433 of localhos to allow HTTPs traffic.

We have to login in the router and go to the *NAT/PAD* that is usually where we can open ports (at least in Orange routers)

#### Dynamic DNS 

As we do not have a static IP configured in our router, but we have a dynamic IP that changes from time to time, we will need a dynamic DNS service for our domain to point to our IP even though it may change.
In this case, I have purchased the domain from IONOS, so this documentation is based on the steps to follow to configure the dynamic DNS service with IONOS as the provider.

The first thing we have to do is to generate an API KEY to be able to interact with the IONOS service. To do this we have to visit the web: https://developer.hosting.ionos.es/?source=IonosControlPanel, go to the IONOS developer section and here we will find an option called manage keys.

<div align="center">
    <img src="./.assets/imgs/ionos-developer.png">
</div>
