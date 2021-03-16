# Manufacture Kubernetes
Découvrir kubernetes en s'a-mu-sant.
L'objectif de ce tuto sera de découvrir les concepts principaux de docker, puis à l'aide de kubernetes, de déployer une API pytho et un front HTML qui appelera cette API.

## Avant propos

Hello, avant de commencer, il serait de bon ton de [télécharger Docker](https://www.docker.com/get-started). On note que l'installation de Docker Desktop comprend directement MiniKube il faudra juste l'activer plus tard. Vous pouvez sinon l'[installer à part](https://minikube.sigs.k8s.io/docs/start/).

Ah et bien sûr, il faut idéalement cloner ce repository. 

### Plait-il ? 

Même si nous allons l'aborder un peu plus loin, une petite présentation de ce que sont Docker et MiniKube peut être utile.

**Docker**: Vous en avez forcément entendu parler, c'est le substitut aux VMs à la mode basé sur le principe de "conteneurisation". L'idée est très simple, prendre un OS vide, mettre uniquement ce dont on a besoin pour son projet dessus, et figer le tout sous forme "d'image" puis l'utiliser pour son projet en le faisant tourner dans un container. Les avantages: 
- assez facile d'utilisation
- on est sûr d'avoir un environnement stable et minimal
- très facile à répliquer à l'identique si besoin

**Kubernetes**: C'est ce qu'on appelle un orchestrateur, un moyen facile de gérer tous ses services, d'automatiser leur déploiements, de les rendre requêtables, de les mettre à l'échelle en fonction de la demande etc. Son lien avec Docker ? Tous les services que l'on déploiera sur Kubernetes (appelé aussi Kube ou K8s) seront des conteneurs. Docker avait à la base développé son propre orchestrateur: Docker Swarm, mais de plus en plus K8s domine le marché. 

**Minikube**: C'est un outil de développement assez pratique qui permet de simuler localement un cluster Kubernetes. En environnement de travail réel, il faudra utiliser un vrai cluster K8S, c'est à dire une vraie plateforme hostée sur un ou plusieurs serveurs permettant d'accéder à un certain nombre de ressources, là où un cluster MiniKube sera limité par les performances de l'ordinateur où il est lancé.

Pas de panique si il y a encore des incompréhensions on va voir tout ça en détail. 

## Mise en place de l'environnement

### Tester Docker

Une fois tout installé, la première étape à effectuer et de vérifier que tout **fonctionne** (ce qui n'est pas toujours gagné non plus). 
Alors pour tester docker, on va télécharger notre première image. 

> Télécharger vous dites ? Mais je croyais qu'on les créait les images ! Oui, mais Docker a aussi un autre énorme avantage: le [DockerHub](https://hub.docker.com), qui est un site permettant d'accéder à des dizaines (centaines?) de milliers d'images Docker déjà toutes faites, et pouvant nous servir de base pour construire les nôtres.

Sur le DockerHub, on va aller chercher "python", le premier lien nous emmène vers le repository docker de python. Un repository c'est un peu comme pour git, un endroit où l'on va stocker les images, et les identifier par des versions plus communément appelées *tags*, une image est donc identifiée par <nom_répertoire>**:**<nom_tag>. Il existe ainsi un certain nombres d'images comme python:3.10, python:3.9.1, python:windows-server etc...  

On pourrait ici prendre le tag par défaut en faisant simplement `docker pull python` mais idéalement je trouve préférable de préciser la version que l'on souhaite avoir de façon explicite: `docker pull python:3.9`.

> Concrètement l'image docker contiendra un OS linux minimal avec la version spécifiée de python d'installée. Et c'est tout.

On peut ensuite tester l'image en elle même en lançant `docker run -it python:3.9` (i pour interactif, t pour tty qui permet d'avoir un affichage décent). Et si tout se passe bien, vous devriez maintenant avoir sous les yeux un splendide interpreteur python n'attendant plus que vos commandes!  

> Comme nous le verrons plus tard si c'est un interpreteur python qui s'ouvre lors du docker run, c'est que la commande qui a été définie dans le Dockerfile de l'image lance l'interpreteur python au démarrage du conteneur. Mais vous pourriez tout aussi bien executer `docker run -it python:3.9 bash` pour vous retrouver à l'intérieur de la machine avec un interpreteur bash et lancer toutes vos commandes linux. 

### Tester Kubernetes

Si vous avez installé docker avec l'installateur docker Desktop, vous pouvez ouvrir l'app, cliquer sur la roue dentée des paramètres -> Kubernetes -> Enable Kubernetes. Cela permettra de démarrer un cluster Kubernetes en local.
Si vous avez installé MiniKube, vous pouvez démarrer le kluster avec `minikube start`.

Pour ensuite tester si votre client kube et le cluster kube fonctionnent bien, vous pouvez lancer `kubectl version`. Ce qui devrait vous afficher une "Client Version" et une "Server Version". Si vous avez effectivement bien les deux, cette partie est donc terminée, et on va pouvoir vraiment commencer. 

## Construire notre image

### Le Dockerfile

L'objectif de cette partie va consister à créer une image Docker contenant notre API. (API dont vous trouverez le code dans api/main.py)
La première étape consiste à créer le [Dockerfile](https://docs.docker.com/engine/reference/builder/), c'est le fichier dans lequel vont être écrites les instructions permettant de construire notre image. 
Un Dockerfile n'a pas d'extension, il s'appelle tout simplement Dockerfile, la plupart des éditeurs de texte modernes le reconnaitront et adapteront la syntaxe automatiquement. 
On va donc se placer dans le répertoire /api et créer un fichier Dockerfile. 

Toutes les images Docker commencent par la même commande: `FROM <nom_d'image>` elle permet d'utiliser une autre image comme base de l'image que l'on créé. 
Si vous avez bien suivi, je vous laisse deviner comment écrire la commande dans notre cas. 
> **Hint:** *si vous bloquez à un moment, tous les fichiers "corrigés" se trouvent sur le git.*

Next step: copier les fichiers de l'api, à l'intérieur de l'image, on va utiliser pour cela l'instruction `COPY` qui va permettre de copier un directory ou un fichier de "l'exterieur" vers un chemin à l'intérieur de container. 

> Par exemple `COPY . .` va copier l'intégralité du répertoire de build (c'est à dire l'endroit où vous aurez lancé votre commande docker build), vers le répertoire courant dans le container. 

Dans notre cas, comme la commande de build sera lancée dans le répertoire api, on copie l'intégralité de `.` dans `./api`. 

La prochaine étape consiste à installer les requirements qui vont permettre de faire tourner notre api: `pip install -r requirements.txt`. Pour lancer cette commande au sein d'un dockerfile, on utiliser la commande RUN. 

Au préalable il faut cependant se placer dans le répertoire `./api` que nous avons créé à l'étape précédente. Il existe pour cela plusieurs méthodes: 
- 1) Utiliser cd en même temps que l'installation: `RUN cd ./api && pip install -r requirements.txt`
- 2) Utiliser `WORKDIR ./api`, l'avantage de cette dernière méthode est qu'elle modifie le répertoire pour toutes les commandes à venir, alors que le cd de l'instruction précédente ne modifie le dossier que pour la durée du `RUN`. On peut ensuite lancer l'installation avec `RUN pip install -r requirements` dans une instruction séparée.  
  
> Il est à noter que dans un docker file, chaque instruction RUN va créer une image intermédiaire qui sera identifiée par un hash, et vous pourrez utiliser chacun de ces hash en tant qu'image indépendante pour tester votre build petit à petit. Mais attention, chaque nouvelle étape intermédiaire va allourdir le poids de votre image finale, il est donc conseillé de combiner les commandes RUN lorsque cela est possible! 

Il ne reste plus qu'à préciser quelle commande lancer lorsque le conteneur sera démarré. En l'occurence, on va ici lancer l'api gunicorn à l'aide de `CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5000"]`.

> Si vous avez choisi la première option lors de l'étape précédente, il faudra préciser api.main:app au lieu de main:app comme vous vous trouverez dans le répertoire parent de ./api.

### Lancer le build

Une fois le dockerfile terminé, il suffit de lancer le build en vous plaçant dans le dossier api et de lancer `docker build .`

> Le `.` dans la commande signifie qu'on lance le build dans le répertoire courant et qu'on envoie tout le contenu de ce répertoire au [docker daemon](https://docs.docker.com/get-started/overview/#the-docker-daemon), qui va utiliser ce dossier dans son contexte d'execution du build. 

Tout devrait se bien se passer et vous obtiendrez à la fin du build un message du type: 

` => => writing image sha256:5563885643d585efd8e30c247b70d784fa6806b5398f41548d1baf613c8efe2c`

Tout ce qui suit `sha256:` s'appelle le hash, vous pouvez vous en servir pour lancer un container avec l'image que vous venez de créer:
`docker run 5563885643d585efd8e30c247b70d784fa6806b5398f41548d1baf613c8efe2c`

Vous devriez à présent voir les logs de démarrage de l'api fastapi. 

Ce docker hash n'étant pas particulièrement pratique à manipuler, on peut déjà utiliser `docker images` pour lister les images et voir le hash réduit dans la colonne `IMAGE ID`.

Mais un moyen encore plus pratique consiste à "tagger" votre image lors du build à l'aide du flag -t. 

`docker build -t <repository_name>:<tag>`

Si le tag n'est pas précisé, l'image sera automatiquement taggée en latest. On peut ainsi lancer dans notre cas:

`docker build -t super_api`

Ce qui permettra ensuite de lancer le container avec:

`docker run super_api`

> Attention, les images sont sauvegardées à chaque build, et des containers sont lancés à chaque docker run (on peut voir les containers lancés à l'aide de `docker ps`), pensez à libérer de l'espace disque en lançant `docker rmi image_hash` ou `docker rmi repository:tag`. Il faudra peut être supprimer les containers utilisant ces images avant avec la commande docker rm container_name. 

### Un dernier problème

Notre application tourne, c'est super. Mais essayez donc de faire un appel get sur votre localhost http://localhost:5000 . SPOILER: ça ne va pas marcher. Et pour cause: il manque deux étapes cruciales à notre process. 
Premièrement, les ports d'un container ne sont pas ouverts de base, il faut manuellement les ouvrir à l'aide de la commande `EXPOSE <port_number>`.

Deuxièmement, docker fait tourner ses containers dans un réseau virtuel, qui n'est pas accessible depuis "l'extérieur", c'est à dire notre localhost. Ainsi le port 5000 du container (TODO: à reformuler). Il faut donc indiquer au docker daemon de mapper le port du container sur un "vrai" port de notre machine à nous. On utilise pour celà le flag `-p <port_reel>:<port_container>`. Ce qui donne chez nous: `docker run -p 8000:5000 super_api.

> Par préférence personnelle j'aime ne pas utiliser exactement le même port réel que le port de container pour distinguer lequel est lequel mais cela n'a aucune importance tant que le port réel n'est pas pris par une autre application. 

Et voilà, vous devriez être en mesure d'appeler maintenant http://localhost:8000 et de voir ce magnifique message apparaître "Hello Unknown".

Il manque cependant la petite touche personnalisée qui ajoute un charme indéniable à notre application; notre nom d'utilisateur. "Unknown" n'est pas bien folichon et on aimerait bien un peu d'originalité. Vous pouvez voir dans le code de l'api que la route / renvoie un hello en fonction de la variable d'environnement "PRENOM" et vaut "Unknown" si cette dernière n'est pas définie. 

Pour la définir on va donc employer deux nouveaux mots clés Docker: `ARG` et `ENV`. Le premier va servir à accepter un argument de build et qui ne sera disponible **que pendant le build**, et le second à set une variable d'environnement. 

On peut ainsi ajouter une ligne à notre Dockerfile avec `ARG PRENOM="valeur_par_defaut". Puis une autre avec `ENV PRENOM $PRENOM` qui va set la variable d'environnement PRENOM avec la valeur de l'ARG définit précédemment.

Si vous rebuildez et lancez à nouveau l'image, le nouveau message retourné par notre API sera "Hello valeur_par_defaut". Ce qui reste fondamentalement décevant. 

Modifions alors notre commande de build: `docker build -t super_api --build-arg PRENOM=SUPERDEVOPS`. Et félicitations, vous venez de transmettre une information à l'intérieur du build et de changer la valeur de la variable d'environnement PRENOM. 

C'est ainsi que se termine cette première partie sur Docker. Nous avons donc une image toute prête qui accueille notre API, et que l'on va maintenant chercher à déployer. 

### Bonus pour aller plus loin: les entry points. 

