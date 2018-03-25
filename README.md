# DeepPet
We use image recognition and web development to assist dog and cat lovers to find/buy/sell their favorite pets.
![alt text](https://github.com/tailongnguyen/petsite/blob/master/gallery/screenshot.png)

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

What things you need to install the software and how to install them

```
python2 (or 3)
django==2.0.3
django-registration-redux
django-notify-x
django-annoying
django-restframework
numpy
pillow
keras
mysql
mysqlclient (python)
```

### Installing

Everything can be installed via pip except for [mysql](https://www.digitalocean.com/community/tutorials/how-to-install-mysql-on-ubuntu-16-04).

## Running
### Initialize the database

First we need to create our database. The default database name the code will look for is "petdatabase", so create a database with that name (Feel free to use other name but make sure you will also modify the code)

After creating the database, migrate the models:
```
python manage.py migrate
```
Everything should be ok.
![alt text](https://github.com/tailongnguyen/petsite/blob/master/gallery/migrate.png)
### Insert the data

Now go back to mysql shell and insert the data:
```
use petdatbase;
source /link/to/petdatabase.sql;
```
and then check the table:
```
select petName from pet_pet;
```
It should give you 94 rows.
### Runserver

Now we can deploy the system on local host:
```
python manage.py runserver
```
and enjoy exploring the site.

## Note

* We have not published our image dataset yet, so there is only information details available on pet pages. You can create your own image dataset and insert them to table pet_petgallery.
* If you use python2 you need to rename the __str__ function in models.py to __unicode__ to ensure the data will be displayed correctly in some pages.

## Authors

* [nguyentailong](https://github.com/tailongnguyen)
* [vutiensinh](https://github.com/vts3497)

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

