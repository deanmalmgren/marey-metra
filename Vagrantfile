# -*- mode: ruby -*-
# vi: set ft=ruby :

# if there are any problems with these required gems, vagrant
# apparently has its own ruby environment (which makes sense). To
# install these gems (iniparse, for example), you need to run
# something like:
#
# [unix]$ vagrant package install iniparse
require 'iniparse'

Vagrant.configure("2") do |config|

  # preliminaries
  root_dir = File.dirname(__FILE__)
  ini = IniParse.parse( File.read(root_dir + '/config.ini') )

  #################################################### VIRTUALBOX PROVIDER SETUP
  # global configuration on the virtualbox provider. for all available
  # options, see http://www.virtualbox.org/manual/ch08.html
  virtualbox_server_name = ini['servers']['virtualbox']
  config.vm.provider :virtualbox do |vb, override_config|
    vb.gui = false
    override_config.vm.box = "trusty64"
    override_config.vm.box_url = "https://cloud-images.ubuntu.com/vagrant/trusty/current/trusty-server-cloudimg-amd64-vagrant-disk1.box"
    override_config.vm.network :forwarded_port, guest: 8000, host: 8000
    # override_config.vm.network :forwarded_port, guest: 80, host: 8080

    # http://stackoverflow.com/a/17126363/892506
    vb.customize ["modifyvm", :id, "--ioapic", "on"]
    vb.customize ["modifyvm", :id, "--cpus", "2"]
    vb.customize ["modifyvm", :id, "--memory", "2048"]
  end

  ################################################################# LOCAL SERVER
  config.vm.define virtualbox_server_name do |server_config|
    server_config.vm.hostname = virtualbox_server_name
  end

end
