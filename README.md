# **kackers-fin-announcer**
Discord bot to announce finishes/PBs for Kacky alike hunting/events in TM20 or TMNF.

Bot can be deployed as a package or simply ran in a Docker container.

Before starting make sure to create a `config.json` based on `example_config.json` template.

---

## **Development**

For development a devcontainer for VSCode has been created.

You need to have following installed to run it:
* *VSCode*
* *Dev Containers extension*
* *Docker*

To run a development container simply open VSCode and Reopen in Container. This will setup two containers (bot & db) and copy all neccessary files and extensions you may need.
You can adjust the created containers by modifying `.devcontainer/devcontainer.json`.

***Note***:
Database files are mapped to local host and will generally be placed in `${PWD}/mariadb`.

In order to be able to rebuild the devcontainer and also allow database user to modify files, you need to update permissions of `mariadb/` folder on your host machine:
* `sudo chown -R ${USER} mariadb/` 
* `sudo chmod 755 -R mariadb/`

This is due to MariaDB container being created with UID & GID of 999 (you can also add Dockerfile for the database container if you wish which sets correct permissions along the way).

Database is created according to the `.devcontainer/init.sql`.

---

## **Deployment**

For deployment a docker-compose has been created in `.deploy`.

TBD


