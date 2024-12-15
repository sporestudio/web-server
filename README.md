# Web Server Deployment

## Project Overview

Automated deployment of a web server made with Docker containers. The server is composed by a main domain with the main page of the web, and serveral subdomains used for two aplications: **an url shortener and a youtube video and audio downloader**. 
We have another two subdomains, one of these for the **grafana monitoring interface** and another one for the **jenkins administration panel**.

## Index

- **Web Server Deployment**
    - [Structure](#structure)
    - [Key Features](#key-features)
    - [Dependencies](#dependencies)
    - [Previous Configurations](#previous-configurations)
    - [Deployment](#deployment-of-the-project)
    - [Web Server Configuration](#web-server-configuration)
    - [Url Shortener](#url-shortener-app)
    - [YouTube Downloader](#youtube-downloader-app)
    - [Grafana Monitoring](#grafana-monitoring-tool)
    - [CI/CD Pipeline](#cicd-pipeline-with-jenkins)
    - [Benchmarks and Tests](#benchmarks-and-tests)
    - [License](#license)
    - [Contribute](#contribute)
    - [Author](#author)

## Structure

```
├── web-server
│   ├── certbot
│   │   ├── htdocs
|   |   |   └── index.html
|   |   └── httpd.conf
|   ├── dyndns
|   |   ├── Dockerfile
|   |   ├── cronjob
|   |   ├── geturl.sh
|   |   └── update.sh
│   ├── url-shortner
|   |   ├── static
|   |   |   └── style.css
|   |   ├── templates
|   |   |   └── index.html
|   |   ├── tests
|   |   |   ├── test_path.py
|   |   |   └── test_unitary.py
|   |   ├── app.py
|   |   ├── dns_manager.py
|   |   ├── Dockerfile
|   |   ├── requirements.txt
|   |   └── widgets.py
|   ├── web
|   |   ├── htdocs
|   |   |   ├── admin
|   |   |   |   └── index.html
|   |   |   ├── assets
|   |   |   ├── styles
|   |   |   |   └── style.css
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
|   ├── .gitignore
|   ├── Jenkinsfile
|   ├── LICENSE
|   ├── Makefile
|   ├── README.md
|   ├── compose.yml
|   ├── prometheus.yml
|   └── test.hurl

```

## Key Features

- Self-hosted deployment leveraging **Docker Compose** for container orchestation.
- Secure access through **HTTPS** via Let's Encrypt certificates and reverse proxy configured with Apache
- System Monitoring with **Grafana**.
- **CI/CD Pipeline** using Jenkins.

> It's important to note that the **CI/CD pipeline** is still under development.

## Dependencies

The required dependecies for deploy the project are:

- **Docker**
- **Python**
- **Docker-compose**
- **Make**

## Previous configurations

### Router configurations

In this project the server will be my personal computer, which does not have a public IP, so we must map port 80 of our router with port 8080 of our machine, as well as port 443 with port 4433 of localhos to allow HTTPs traffic.

<div align="center">
    <img src="./.assets/img/router2.png">
</div>

We have to login in the router and go to the *NAT/PAD* that is usually where we can open ports (at least in Orange routers)

<div align="center">
    <img src="./.assets/img/router1.png">
</div>

#### Dynamic DNS 

As we do not have a static IP configured in our router, but we have a dynamic IP that changes from time to time, we will need a dynamic DNS service for our domain to point to our IP even though it may change.
In this case, I have purchased the domain from IONOS, so **this documentation is based on the steps to follow to configure the dynamic DNS service with IONOS as the provider**.

The first thing we have to do is to generate an API KEY to be able to interact with the IONOS service. To do this we have to visit the web: https://developer.hosting.ionos.es/?source=IonosControlPanel, go to the IONOS developer section and here we will find an option called manage keys.

<div align="center">
    <img src="./.assets/img/ionos-developer.png">
</div>

Once we have our API Key we have to go the [DNS documentation section](https://developer.hosting.ionos.es/docs/dns) and authorize the service with our API Key.

<div align="center">
    <img src="./.assets/img/authorize1.png">
</div>


<div align="center">
    <img src="./.assets/img/authorize2.png">
</div>

We must make a POST request with our API Key and our domains and we will receive the url in JSON format.

```json
{
  "bulkId": "e0d3db69-19cc-449a-aca0-7fb4b69ba774",
  "updateUrl": "https://ipv4.api.hosting.ionos.com/dns/v1/dyndns?q=YTFmN2Q5Y2VkYmQ0NDE2OWJlZDEwNDBiZDRlNTFlNTkuUTNPaWJTaG1rMnBpUVVoMUhlcDdlVWpyZ2Mxb0J0MEdsbHZrSWF6dzVlTURZMjZON2VtUlFKS1k2SFhfeEVMaEs1Y1cyRjJvV1NhcUhTajVUNVlSYlE",
  "domains": [
    "sporestudio.me",
    "www.sporestudio.me"
  ],
  "description": "My DynamicDns"
}
```

>[!NOTE]
> We can obtain the update url automatically executing the geturl.sh script, you just change the fields of the API Key with your code and change my domains to yours.

<div align="center">
    <img src="./.assets/img/geturl.jpeg">
</div>

To make sure that the IP is always update we encapsulated this service in a docker container that is running cron updating the IP address every minute. We've created an image using the official Docker's Debian image where we copy the script `update.sh` to the container and a crontab will be running the script every minute.

<div align="center">
    <img src=".assets/img/update.sh">
</div>

This script will be running in our Docker container as a service, so we've created a docker image for it.

```Dockerfile
FROM debian:12.8
RUN apt-get update && apt-get -y install cron curl

WORKDIR /app

COPY update.sh update.sh
COPY update_url update_url
RUN chmod +x update.sh

COPY cronjob /etc/cron.d/cronjob
RUN chmod 0644 /etc/cron.d/cronjob
RUN crontab /etc/cron.d/cronjob

CMD ["cron", "-f", "/etc/cron.d/cronjob"]
```

### Install dependencies for the project

Before deploy the project we have to install the necessary dependencies for our apps.

#### Install url-shortener dependencies

We have to navigate to the app directory and create a virtual enviroment (optional but recommended).

```bash
$ cd url-shortener/
$ python -m venv venv
$ source venv/bin/activate
```

Now install dependencies with `pip install`.

```bash
$ pip install -r requirements.txt
```


#### Install web-downloader dependencies

The steps to install the dependencies of web-downloader will be the same, we have to navigate to web-downloader directory and install the dependencies with `pip install`.

```bash
$ cd web-downloader/
$ python -m venv venv
$ source venv/bin/activate
$ pip install -r requirements.txt
```

### Create .env file

You will need to create a `.env` file with the following fields for the project to work.

```bash
# FLASK Configuration
FLASK_APP=

# IONOS API Configuration
IONOS_BASE_URL=
IONOS_API_KEY=

# Apache global vars
DOMAIN_NAME=
GRAFANA_DOMAIN=
DOMAIN_ID=
SERVER_ADMIN=

STATUS_PASSWD=

# Variables for Jenkins configs
JENKINS_URL=
JENKINS_AGENT= 
JENKINS_SECRET=
```

>[!CAUTION]
> Never commit sensitive values to control version.


## Deployment of the project

We have several ways to deploy this project, one of them using the `Makefile` or using `docker-compose`.

### Using Makefile

- Deploy the server and generate/renew SSL certificates:

```bash
$ make all
```

- Deploy without generating new certificates:

```bash
$ make deploy
```

### Using docker-compose

- Deploy the server building the docker images.

```bash
$ docker-compose up --build -d
```

## Web server configuration

### Obtain the SSL certificates via Cerbot

In order to provide a safe and encrypted connection to our server, we will need a valid certificate. We will do using [certbot](https://hub.docker.com/r/certbot/certbot) which is a docker image provide by [**Let's Encrypt**](https://letsencrypt.org/es/), an open and free certificate authority.

Cetbot uses the ACME (Automatic Certificate Management Enviroment)  protocol, provided by Let's Encrypt to obtain and renewing the SSL certificates.

#### How Certbot and ACME work together

1. **Domain Ownership Validation**:
    - Certbot proves to the Let's Encrypt Certificate Authority (CA) that you control the domain for which you are requesting an SSL certificate.

    - The ACME protocol facilitates this validation process.

2. **Validation method**: Certbot uses severals methods to complete domain validation, in our case, we're going to explain the HTTP-01 Challenge that is what we used in this project, to more info about the other methods you can check the [certbot official documentation](https://eff-certbot.readthedocs.io/en/stable/).

    - **HTTP-01 Challenge**: Is a method used by Certbot and other ACME clients to validate domain ownership for *SSL/TLS* certificate issuance. It works by creating a unique token and placing it in a specific file (`/.well-known/acme-challenge/*TOKEN*`) on your server. 
    
        The Certificate Authority (CA), such as Let's Encrypt, then makes an HTTP request to retrieve this file and confirm its contents. If the file is correctly served, the CA verifies that you control the domain and issues the certificate. This method requires the domain to be publicly accessible via HTTP (port 80) but is simple to automate, making it ideal for many web servers.

3. **Certificate Issuance**:
    - Once ownership is confirmed, Let's Encrypt issues an *SSL/TLS* certificate for your domain.

    - Certbot downloads and configures this certificate, usually placing the files in `/etc/letsencrypt/live/<yourdomain>/`.

4. **Automatic Renewal**:
    - Certificates from Let's Encrypt are valid for 90 days.

    - Certbot includes a built-in renewal mechanism *(certbot renew)*, which ensures your certificates remain valid without manual intervention.

So in this project to obtain the SSL certificates I've created a temporary web server listening on port 80 with the domain we want to certificate, and once the server is listening on port 80, we will run the certbot container to obtain the certificates:

<div align="center">
    <img src=".assets/img/makefile.jpeg">
</div>

> [!NOTE]
> The certificates will be created on the container's directory `/etc/letsencrypt`, so we created a permanent docker volume called **certs** to preserve it.

### Apache configuration

The main web server will be running in a Docker container with the official image of Apache: [**httpd**](https://hub.docker.com/_/httpd)

```yaml
web:
    image: httpd:latest
    container_name: web
    env_file:
        - .env
    volumes:
        - ./web/htdocs:/usr/local/apache2/htdocs
        - ./web/httpd.conf:/usr/local/apache2/conf/httpd.conf
        - ./web/httpd-vhosts.conf:/usr/local/apache2/conf/extra/httpd-vhosts.conf
        - certs:/etc/letsencrypt
    ports:
        - 8080:80
        - 4433:443
```

As we can see we map the certs docker volume to the container directory **/etc/letsencrypt**. The certificates will be located at `/etc/letsencrypt/live/[your-domain]/fullchain.pem` and `/etc/letsencrypt/live/[your-domain]/privkey.pem`

#### Virtual hosts configuration

**The server have several virtual hosts configured**, one is for the main server, and we have another four virtual hosts, two of them for the applications **url shortener and youtube downloader**, other for the **Grafana monitoring system** and another one for the **Jenkins administration panel**.

##### Reverse proxy configuration

**Apache acts as an intermediary**, forwarding external client requests to the internal services, allowing this services to remain isolated from direct public access.

How can see for example in the virtual host for the url shortener application, we forward HTTP requests to the internal service at `http://url-shortener:5000/`.

<div align="center">
    <img src=".assets/img/shortener-vhost.jpeg">
</div>

## Url shortener app

The url shortener app is a web service deployed as part of the self-hosted infrastructure at `https://url.sporestudio.me`. Its primary purpose is to simplify lengthy URLs into compact links, making them easier to share or manage.

### Key features
-  **Custom Shortened URLs**: Converts longs URLs into concise, shareable links.

- **Hash-Based Identification**: Uses a hashing algorithm (SHA-256) to generate unique codes for each URL.

- **Persistent Storage**:Ensures that shortened links are stored in a database for retrieval and analytics.

- **Redirect Service**: Automatically redirects users from the short link to the original, full URL.

### Technology Stack
- **Backend**:
    - Built using **Python** with the [**Flask**](https://flask.palletsprojects.com/en/stable/) web framework.

    - Implements cryptographic functions via the [hashlib](https://docs.python.org/3/library/hashlib.html) library for generating unique hash codes for URLs.

- **Frontend**: A minimal interface for submitting URLs, generating shortened links, and monitoring usage.

- **Database**: In this case we've used the IONOS **DNS server** as database, storing the links as **TXT type records** within the server.

- **Reverse Proxy**: Managed through Apache, which handles HTTP(S) requests to the app.


### Workflow

First the users **submit a long URL** through the app interface.

<div align="center">
    <img src=".assets/img/urlshort-interface.png">
</div>

Then we catch this long url input by the users via form through POST method. To this long url we apply a function that generates a **hash of 6 alphanumeric characters**, which will be our short url, and using the function of our library [dns_manager.py](https://github.com/sporestudio/web-server/blob/main/url-shortener/dns_manager.py), created by us, we create a **TXT record in the DNS server with the shortened url** and then print it in the `index.html` using the **render_template** function of Flask.

```python
def shortener_url(original_url):
    return hashlib.sha256(original_url.encode()).hexdigest()[:6]


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        original_url = request.form['url']
        short_url = shortener_url(original_url) 
        
        if create_txt_record(short_url, original_url):
            url_shortener = f"https://url.{DOMAIN_NAME}/{short_url}"
            return render_template('index.html', short_url=url_shortener, original_url=original_url)
        else:
            return "Error creating DNS TXT record", 500

    return render_template('index.html')
```

Finally **we have to handle the redirection** from the short url to the long url making use again of the [dns_manager.py](https://github.com/sporestudio/web-server/blob/main/url-shortener/dns_manager.py) library, where we make a DNS query so that if there is a TXT record for that short url we redirect it to the value of that record (which is the original url).

```python
@app.route('/<short_url>')
def redirect_url(short_url):
    original_url = get_original_url(short_url)
    if original_url:
        return redirect(original_url)
    else:
        return "Short url not found", 404
```

### Tests

We have created some tests that guarantee the performance and uniformity of the application code. For this I have used the Pytest library that allows you to create tests for your application easily in a few lines of code.

#### Path test

- **Purpose**: Verifies that the application's main page is accessible and displays the correct content.

- **Details**: 

    - **Tested Funcionality**: Sends a GET request to the home (/) route.

    - **Assertions**: 

        - The HTTP status code of the response is 200, indicating the page loaded successfully.

        - The response contains the text URLs shortener, confirming the main page displays the intended content.

```python
import pytest
from app import app

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

def test_home_path(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"URLs shortener" in response.data
```

#### Short URL Genereation Test

- **Purpose**: Ensures the `shortener_url` function generates valid, unique short URLs.

- **Details**: 

    - **Tested Funcionality**: Calls the `shortener_url` function with a sample URL as input.

    - **Assertions**: 

        - The generated short URL is exactly 6 characters long, as per the application's design.

        - The short URL is alphanumeric, ensuring it is user-friendly and URL-compatible.

```python
import pytest
from app import shortener_url

def test_generate_short_url():
    original_url = "https://example.com"
    short_url = shortener_url(original_url)
    assert len(short_url) == 6
    assert short_url.isalnum()
```

#### How to run the tests

1. Ensure that all dependencies are installed. Navigate to url-shortener directory, create a virtual enviroment and activate it (optional but recommended).

```bash
$ cd url-shortener/
$ pyhton3 -m venv venv
$ source venv/bin/activate
```

2. Then install the dependencies from the `requirements.txt` with pip.

```bash
$ pip install -r requirements.txt
```

3. Run the tests.

```bash
$ pytest
```

<div align="center">
    <img src=".assets/img/pytest.png">
</div>

## YouTube downloader app

**YouTube downloader** application is a Python-based tool using [Flask](https://flask.palletsprojects.com/en/stable/) for the web server and [pytubefix](https://github.com/JuanBindez/pytubefix) (I had some issues with pytube lib) for handling YouTube video downloads.

### Key features

- **Web Interface**: A simple page where users can paste the YouTube url and select the quality of the video or even just download the audio.

- **Video Quality Options**:
    
    - **Highest**: Downloads the video in the highest available resolution.

    - **Lowest**: Downloads the video in the lowest available resolution.

    - **Audio**: Downloads only the audio stream (useful for music or podcasts).

- **Temporary File Management**: Downloads the file to a temporary location and deletes it after serving it to the user `(os.remove(output_path))`.

### Workflow

The main function of the app uses route `/download` that defines the URL endpoint where the video download process is handled. When the user interacts with the webpage, such as by submitting a form to download a video, the browser sends a POST request to the `/download` URL.

```python
@app.route('/download', methods=['POST'])
def down_video():
    url = request.form['url']
    quality = request.form['quality']
    try:
        yt = YouTube(url)

        if quality == 'highest':
            stream = yt.streams.get_highest_resolution()
        elif quality == 'lowest':
            stream = yt.streams.get_lowest_resolution()
        elif quality == 'audio':
            stream = yt.streams.filter(only_audio=True).first()
        else:
            return "Invalid quality selected"
    
        output_path = stream.download()
        response = send_file(output_path, as_attachment=True, download_name=f"{yt.title}.{stream.subtype}")
        os.remove(output_path)
        return response
    except Exception as e:
        return f"An error occurred: {str(e)}"
```

Then we extracting the user input from the form and the quality specified. As we can see we have to create a **YouTube object** for the provided URL using `pytubefix` library.

We select the appropriate stream for downloading and the path of the downloaded file is stored in **output_path** varibale. To finish we send the file to the user.

## Grafana monitoring tool

To provide our server with monitor functions, we will use [Grafana](https://grafana.com/docs/grafana/latest/) in combination with [Prometheus](https://prometheus.io/docs/visualization/grafana/) and [apache_exporter](https://github.com/Lusitaniae/apache_exporter).

We will use apache_exporter to scrape data from **/status** (`mod_status`) and transform this data into a format that Prometheus can understand. 

So we will use the official apache exporter image from **Docker Hub** to create the apache exporter container.

> We will pass the URL where we allocated the `mod_status` and the authentication.

```yaml
apache-exporter: 
    image: lusotycoon/apache-exporter
    container_name: apache-exporter
    depends_on:
      - web
    privileged: true
    expose:
      - 9117
    restart: unless-stopped
    extra_hosts:
    - "localhost:127.17.0.1"
    env_file:
      - .env
    entrypoint: /bin/apache_exporter --scrape_uri="https://sysadmin:${STATUS_PASSWD}@sporestudio.me/status?auto/"
```

Now we have to configure the `prometheus.yml` to indicate the socket of the host that have the data we want to display. In our case, *apache_exporter:9117*.

> [!NOTE]
> Since we have all the containers in the same compose file, docker-compose will resolve the addresses for us.

```yaml
# my global config
global:
  scrape_interval: 1m 

# A scrape configuration containing exactly one endpoint to scrape:
scrape_configs:
  - job_name: "apache_exporter"
    static_configs:
      - targets: ["apache-exporter:9117"]
```
* *prometheus.yml*

Once we have this configured, we have to create the container for Prometheus service, we are using the official Prometheus image from **Docker hub**.

```yaml
prometheus:
    image: prom/prometheus
    container_name: prometheus
    depends_on:
      - apache-exporter
    restart: unless-stopped
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
      - '--web.enable-lifecycle'
    expose:
      - 9090
```

> *Prometheus will be listen in port 9090*.

### Grafana configuration

Last but not least, we have to configure the grafana container using the official image from, again, Docker Hub.

```yaml
grafana:
    image: grafana/grafana
    container_name: grafana
    expose:
      - 3000
    volumes:
      - grafana_data:/var/lib/grafana
```

I've created a virtual host for garafana to can configure it from a subdomain within my page. Here is the configuration for this subdomain:

<div align="center">
    <img src=".assets/img/grafana-domain.jpeg">
</div><br/>


So now when we visit https://grafana.sporestudio.me we access the grafana login panel.


<div align="center">
    <img src=".assets/img/grafana-login.png">
</div><br/>


Once inside Grafana we have to navigate to **Menu > Connections > Add new connection**, and here we have to select *Prometheus* as data source.


It is important to note that the **URL in our case is the name of the Docker container** with the prometheus service, since docker compose will resolve the IPs for us.



<div align="center">
    <img src=".assets/img/prometheus-connect.png">
</div><br/>


Once we save and test the data source connection, we have to see a message like this:


<img src=".assets/img/successful.png">

> *Successful connection*.

After complete the connection, we can create our dashboard with the apache exporter instances that we choose.

<div align="center">
    <img src=".assets/img/grafana-data.png">
</div>

## CI/CD Pipeline with Jenkins

> [!WARNING]
> This service is still under developoment.

## Benchmarks and Tests

### Apache Benchmark

[Apache Benchmark](https://httpd.apache.org/docs/2.4/programs/ab.html) was used to evaluate server's performance. Several tests have been applied to the main page and its paths.

#### 100 clients and 1000 requets

With the *-k* flag:

- **sporestudio.me/**

```bash
$ ab -f SSL3 -k -c 100 -n 1000 -H "Accept-Encoding: gzip, deflate" https://sporestudio.me
```

<div align="center">
    <img src=".assets/img/test1-ab.png">
</div>


<div align="center">
    <img src=".assets/img/test-ab22.png">
</div><br/>


- **sporestudio/admin**

```bash
$ ab -f SSL3 -k -c 100 -n 1000 -A admin:{passwd} -H "Accept-Encoding: gzip, deflate" https://sporestudio.me/admin
```

<div align="center">
    <img src=".assets/img/admin-ab.png">
</div><br/>


Without *-k* flag:

- **sporestudio.me/**

```bash
$ ab -f SSL3 -c 100 -n 1000 -H "Accept-Encoding: gzip, deflate" https://sporestudio.me
```

<div align="center">
    <img src=".assets/img/nok-ab.png">
</div><br/>

- **sporestudio/admin**

```bash
$ ab -f SSL3 -c 100 -n 1000 -A admin:{passwd} -H "Accept-Encoding: gzip, deflate" https://sporestudio.me/admin
```

<div align="center">
    <img src=".assets/img/nok-admin.png">
</div><br/>


#### 1000 clients and 10000 requests

With *-k* flag:

- **sporestudio.me/**

```bash
$ ab -f SSL3 -k -c 1000 -n 10000 -H "Accept-Encoding: gzip, deflate" https://sporestudio.me
```


<div align="center">
    <img src=".assets/img/ab-test5.png">
</div><br/>


- **sporestudio/admin**

```bash
$ ab -f SSL3 -k -c 1000 -n 10000 -A admin:{passwd} -H "Accept-Encoding: gzip, deflate" https://sporestudio.me/admin
```

<div align="center">
    <img src=".assets/img/admin-abtest5.png">
</div><br/>


Without *-k* flag:

- **sporestudio.me/**

```bash
$ ab -f SSL3 -c 1000 -n 10000 -H "Accept-Encoding: gzip, deflate" https://sporestudio.me
```


<div align="center">
    <img src=".assets/img/nok-1000.png">
</div><br/>


- **sporestudio/admin**

```bash
$ ab -f SSL3 -c 1000 -n 10000 -A admin:{passwd} -H "Accept-Encoding: gzip, deflate" https://sporestudio.me/admin
```

<div align="center">
    <img src=".assets/img/admin-nok1000.png">
</div><br/>


#### Conclusions

- We can see that if we enable the Keep-Alive connections (*-k*), tests significantly improves performance.

- Adding headers helped reduce overall bandwidth usage but didn’t entirely mitigate server overload.

- The test with 100 clients concurrency shows the highest Requests per Second and the lowest Time per Request, indicating improved efficiency at lower concurrency levels. 

### Hurl

We can run a test with [hurl](https://hurl.dev/) that performs GET requests to our website and different subdomains, to check that they exist.

```bash
# Index page exists
GET https://{{site}}/
HTTP 200

# Logo exists
GET https://{{site}}/logo.png
HTTP 200

# Administration
GET https://{{site}}/admin
[BasicAuth]
admin: asir

# Status
GET https://{{site}}/status
[BasicAuth]
sysadmin: risa

# Url shortener subdomain
GET https://url.{{site}}
HTTP 200

# YouTube downloader subdomain
GET https://downs.{{site}}
HTTP 200
```

<div align="center">
    <img src=".assets/img/hurl-test.png">
</div><br/>

## License

This project is under <a href="https://github.com/sporestudio/web-server/blob/main/LICENSE">GNU General Public License v3.0</a>.

## Contribute

Want to contribute? There are multiple ways you can contribute to this project. Here are some ideas:

* [Translate the web into multiple languages!](./CONTRIBUTING.md#translations)
* [Fix some easy issues](CONTRIBUTING.md#Reporting-Issues)
* [Or check out some other issues](CONTRIBUTING.md#Reporting-Issues) (or translate them).

## Author

Created by <a href="https://github.com/sporestudio/">sporestudio</a>.
