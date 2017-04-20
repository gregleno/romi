recompile cwiid
sudo cp cwiid.so /usr/lib/python2.7/dist-packages/cwiid.arm-linux-gnueabihf.so

sudo cp rominet.service /lib/systemd/system/rominet.service
sudo chmod 644 /lib/systemd/system/rominet.service
# cp  service.py a_star.py wiiremote.py robot_controler.py /home/ubuntu/robot/

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
