# RPB202 program template

# Import libraries
import sys
import robotbuilder
sys.path.append('../')

# Create Robot object instance
rpb202 = robotbuilder.build()

try:
    print "Add main program here"
except KeyboardInterrupt:
    print "Keyboard Interrupt"
    rpb202.stop()
    rpb202.kill()

finally:
    rpb202.stop()
    rpb202.kill()
