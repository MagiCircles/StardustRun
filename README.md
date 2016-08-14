StardustRun
===========

The Pokémon GO Sharing Community

Get Started
-----------

- Install pre-requirements

  - Debian, Ubuntu, and variants

    ```shell
    apt-get install libpython-dev libffi-dev python-virtualenv libmysqlclient-dev nodejs
    ```

  - Arch

    ```shell
    pacman -S libffi python-virtualenv libmysqlclient nodejs
    ```

- Clone the repo

  ```shell
  git clone https://github.com/SchoolIdolTomodachi/StardustRun.git
  cd StardustRun
  ```

- Create a virtualenv to isolate the package dependencies locally

  ```shell
  virtualenv env
  source env/bin/activate
  ```

- Install packages (including [MagiCircles](https://github.com/SchoolIdolTomodachi/MagiCircles))

  ```shell
  pip install --upgrade setuptools
  pip install -r requirements.txt
  ```

- Create tables, initialize database

  ```shell
  python manage.py migrate
  ```

- Create the initial database of Pokémon (optional)

  ```shell
  pip install beautifulsoup4
  pip install html5lib
  python manage.py import_serebii
  ```
  You may use "noimages" after "import_serebii" to make it faster

- Generate the generated settings

  ```shell
  python manage.py generate_settings
  ```

- Get the static files

  ```shell
  git clone https://github.com/SchoolIdolTomodachi/StardustRun-Static.git
  mv StardustRun-Static stardustrun/static
  ```

- Download front-end dependencies

  ```shell
  npm install -g bower
  bower install
  ```

- Launch the server

  ```shell
  python manage.py runserver
  ```

- Open your browser to [http://localhost:8000/](http://localhost:8000/) to see the website


## More

- Compile localized messages

  ```shell
  python manage.py compilemessages
  ```

- Fill the map with users locations

  ```shell
  python manage.py latlong
  ```
