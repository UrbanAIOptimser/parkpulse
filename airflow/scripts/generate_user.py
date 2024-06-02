import airflow
from airflow import models, settings
from airflow.contrib.auth.backends.password_auth import PasswordUser

user = PasswordUser(models.User())
user.username = "JohnOMDev"
user.email = "john.omole@bts.tech"
user.password = "bdi-FinalProject30"
session = settings.Session()
session.add(user)
session.commit()
session.close()
exit()


airflow users create \
    --username JohnOMDev \
    --firstname john \
    --lastname omole \
    --role Admin \
    --email john.omole@bts.tech
    --password bdi-FinalProject30


airflow users create -r Admin -u john_dev -e john.omole@bts.tech -f john_adetoyese -l omole -p bdi-FinalProject30


airflow users create \
          --username admin \
          --firstname john \
          --lastname john \
          --role Admin \
          --email john.omole@bts.tech



{
  "aws_access_key_id": "ASIAXY6H6YTVVURM426A",
  "aws_secret_access_key": "uHCl11cKYISiVv44Ss67Z+3EP0AhaJeCxdWCjZgM"
}