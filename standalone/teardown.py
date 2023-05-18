import os
 
os.system("docker-compose down")
os.system("docker volume rm installers_atlasvolume")
os.system("docker volume rm installers_sqlvolume")
os.remove("standalone/atlas.env")
os.remove("db.env")
os.remove("docker-compose.yml")