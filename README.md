StardustRun
===========

The Pokémon GO Sharing Community

Get Started
-----------

```
# Install pre-requirements
# Debian, Ubuntu, and variants
apt-get install libpython-dev libffi-dev python-virtualenv libmysqlclient-dev nodejs
# Arch
pacman -S libffi python-virtualenv libmysqlclient nodejs

# Clone the repo
git clone https://github.com/SchoolIdolTomodachi/StardustRun.git
cd StardustRun

# Create a virtualenv to isolate the package dependencies locally
virtualenv env
source env/bin/activate

# Install packages, no need to be root
pip install --upgrade setuptools
pip install -r requirements.txt

# Create tables, initialize database
python manage.py migrate

# Create the initial database of pokémons (optional)
python manage.py import_serebii

# Generate the generated settings
python manage.py generate_settings

# Compile localized messages
python manage.py compilemessages

# Download front-end dependencies
npm install -g bower less
bower install

# Launch the server
python manage.py runserver

# Then open your browser to http://localhost:8000 to see the website
```
