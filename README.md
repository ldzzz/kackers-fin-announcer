# **kackers-fin-announcer**
Discord bot to announce finishes/PBs for Kacky alike hunting/events in TM20 or TMNF.

Bot is deployed as a Docker container.

---

## **Development**

For development a devcontainer for VSCode has been created.

You need to have following installed to run it:
* *VSCode*
* *Dev Containers extension*
* *Docker*

To run a development container simply open VSCode and Reopen in Container. This will setup two containers (bot & db) and copy all neccessary files and extensions you may need.
You can adjust the created containers by modifying `.devcontainer/devcontainer.json`.

---

## **Deployment**

For deployment a docker-compose has been created in `.deploy`.
`.deploy/docker-compose.yml` is reading the environment variables from the `.deploy/.env`. You need to create this file and place it within `.deploy`. 
Take a look at `example.env` as a reference.
Additionally, you can setup the bot with some additional configuration. Hence, make sure to create a `config.json` based on `example_config.json` template.

To deploy the bot, run: `docker compose -p finannouncer -f .deploy/docker-compose.yml up -d`
