# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|
  config.vm.box = "debian/bookworm64"
  config.vm.box_check_update = false
  config.ssh.insert_key = false
  config.vm.provider :virtualbox do |vb|
    vb.memory = 256
    vb.cpus = 2
  end

  config.vm.define "web" do |web|
    web.vm.hostname = "web"
    web.vm.network "public_network", ip: "192.168.57.10", bridge: "eth0"
    web.vm.network "forwarded_port", guest: 80, host: 8080
    web.vm.network "forwarded_port", guest: 443, host: 4433

    web.vm.provision "shell", inline: <<-SCRIPT 
      apt-get update && apt-get upgrade
      apt-get install -y apache2 curl jq
      mkdir -p /home/vagrant/dyndns
      cp -v /vagrant/dyndns/cronjob /etc/cron.d/cronjob
      cp -v /vagrant/dyndns/geturl.sh /home/vagrant/dyndns/
      cp -v /vagrant/dyndns/update.sh /home/vagrant/dyndns/
      chmod +x /home/vagrant/dyndns/geturl.sh
      /home/vagrant/dyndns/geturl.sh
      chmod +x /home/vagrant/dyndns/update.sh
      chmod 0644 /etc/cron.d/cronjob
    SCRIPT
  end

  config.vm.define "api" do |a|
    a.vm.hostname = "api"
  end
end



