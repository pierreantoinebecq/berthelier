# Démarrer tout et voir les logs 
up:
	docker compose up --build

# Démarrer en arrière-plan 
up_d:
	docker compose up --build -d

# Arrêter tout (Le bouton OFF)
down:
	docker compose down

# Entrer dans le conteneur pour taper des commandes
shell:
	docker compose exec app /bin/bash

# Lancer le script de test manuellement
test:
	docker compose exec app python test.py

# Lancer un notebook Jupyter 
notebook:
	docker compose exec app jupyter notebook --ip 0.0.0.0 --port 8888 --no-browser --allow-root