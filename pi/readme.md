recompile cwiid
sudo cp cwiid.so /usr/lib/python2.7/dist-packages/cwiid.arm-linux-gnueabihf.so

sudo cp robot.service /lib/systemd/system/robot.service
sudo chmod 644 /lib/systemd/system/robot.service
cp  robot_service.py a_star.py wiiremote.py robot_controler.py /home/ubuntu/robot/

sudo systemctl daemon-reload
sudo systemctl enable robot.service
sudo systemctl start robot.service

# Check status
sudo systemctl status robot.service

# Start service
sudo systemctl start robot.service

# Stop service
sudo systemctl stop robot.service

# Check service's log
sudo journalctl -f -u robot.service
