# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|

  config.vm.box = "ubuntu/xenial64"
  config.vm.hostname = "yleq-box"

  config.vm.provision "shell", inline: <<-SHELL
    apt-get update
    locale-gen en_US.UTF-8 fi_FI.UTF-8
    apt-get install -y \
      python-pip \
      ffmpeg \
      curl \
      php7.0-cli \
      php7.0-bcmath \
      php7.0-curl \
      php7.0-xml \
      rtmpdump \
      sqlite3 \
      python-sqlite \
      python-click \
      python-tabulate
    pip install yle-dl
  SHELL

  config.vm.provision "shell", privileged:false, inline: <<-SHELL
    cd /vagrant
    python yleq.py db-create
  SHELL

end

