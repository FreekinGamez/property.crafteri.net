import sys
import logging
logging.basicConfig(stream=sys.stderr)

sys.path.insert(0, '/var/www/property/www')

from app import app as application  # Critical: "application" name
