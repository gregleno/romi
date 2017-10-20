.. image:: https://travis-ci.org/gregleno/romi.svg?branch=master
    :target: https://travis-ci.org/gregleno/romi


recompile cwiid
sudo cp cwiid.so /usr/lib/python2.7/dist-packages/cwiid.arm-linux-gnueabihf.so

sudo cp rominet.service /lib/systemd/system/rominet.service
sudo chmod 644 /lib/systemd/system/rominet.service
# cp  service.py a_star.py wiiremote.py robot_controler.py /home/ubuntu/robot/

By default, I2C runs at 100 kHz, but you can safely increase that rate to 400 kHz and get a much faster communications
channel between the boards. To increase the speed, edit the configuration file in /boot/config.txt and set:
dtparam=i2c_arm_baudrate=400000

sudo systemctl daemon-reload
sudo systemctl enable rominet.service
sudo systemctl start rominet.service

# Check status
sudo systemctl status rominet.service

# Start service
sudo systemctl start rominet.service

# Stop service
sudo systemctl stop rominet.service

# Check service's log
sudo journalctl -f -u rominet.service

Robot control:
   press wii button B and button 1 to stop:
