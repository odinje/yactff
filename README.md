# Yet Another CTF Framework (YACTFF)

A web framework for Jeoprody style CTF.

## Getting Started

Below is documentation for setting up a development environment for YACTFF.

[Screenshots](https://github.com/odinje/yactff/wiki/Screenshots)

### Prerequisites

* Python 3.
* Pip3

### Installing and running

```
virtualenv -p python3 yactff
source yactff/bin/activate
pip install -r requirements.txt
pip install -r requirements_dev.txt # Django toolbar 
python ./manage.py migrate --setting=yactff.settings.development
python ./manage.py runserver --setting=yactff.settings.development
```

## Running the tests

TODO!

## Built With

* [Django](https://www.djangoproject.com/) - The web framework used
* [Bootstrap](https://getbootstrap.com/) - Bootstrap is an open source toolkit for developing with HTML, CSS, and JS.

## License

This project is licensed under the MIT License - see the [LICENSE.txt](LICENSE.txt) file for details
