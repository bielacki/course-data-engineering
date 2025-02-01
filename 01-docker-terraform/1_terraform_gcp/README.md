# Terraform

Infrastructure as code.

Can be istalled globally via `homebrew`.

```bash
brew install terraform
```

Providers (~platforms):
- GCP
- AWS
- Azure
- etc.

## Main commands

* #### Prepare your working directory for other commands:
    ```python
    terraform init
    ```

* #### Check whether the configuration is valid
    Validate the configuration files in a directory, referring only to the configuration and not accessing any remote services such as remote state provider APIs, etc.

    ```python
    terraform validate
    ```

* #### Show changes required by the current configuration
     Generates a speculative execution plan, showing what actions Terraform would take to apply the current configuration. This command will not actually perform the planned actions.

    ```python
    terraform plan
    ```

* #### Create or update infrastructure
    Creates or updates infrastructure according to Terraform configuration files in the current directory.

    ```python
    terraform apply
    ```

* #### 
    -

    ```python
    terraform destroy
    ```


* #### Reformat config files to a canonical format
    All configuration files (`.tf`), variables files (`.tfvars`), and testing files (`.tftest.hcl`) in a working directory.

    ```python
    terraform fmt
    ```

## Create GCP service account

Go to IAM & Admin -> Service account -> Create service account.

Give it the following Roles:
- Storage Admin
- BigQuery Admin
- Compute Admin

Click Manage Keys -> Add a new key -> Key type: JSON

! Save to /secrets/ directory, and add `secrets/` to the `.gitignore`.

! Important - add .terraform 

## Create Terrafom config files

Create main.tf file.

To get sarte with the `main.tf` structure, go to https://registry.terraform.io/providers/hashicorp/google/latest/docs/guides/getting_started, click **Use provider** and copy-paste sample structure into `main.tf`.

Example:

```tf
terraform {
  required_providers {
    google = {
      source = "hashicorp/google"
      version = "6.18.1"
    }
  }
}

provider "google" {
  # Configuration options
}
```

Then copy config options:

```
provider "google" {
  project = "{{YOUR GCP PROJECT}}"
  region  = "us-central1"
  zone    = "us-central1-c"
}
```

Specify path to the service account in the credentials parameter:

```
credentials = "<path-to-the-service-account-key>.json"
```

Run `terraform fmt` to format **main.tf**.

Now we need to run `terraform init` to initialize provider specified in the `main.tf`.

```bash
terraform init
```

After running init we can see new folders and files created in our working directory:
- `.terraform/` directory containing providers specified in the `main.tf` file
- `.terraform.lock.hcl` file

Let's create a Cloud Storage bucket.

To find a code exampe just google "terraform gcs bucket" and copy configuration from here:

```
resource "google_storage_bucket" "demo-bucket" {
  name          = "course-data-engineering-demo-bucket"
  location      = "US"
  force_destroy = true

  lifecycle_rule {
    condition {
      age = 3
    }
    action {
      type = "Delete"
    }
  }

  lifecycle_rule {
    condition {
      age = 1
    }
    action {
      type = "AbortIncompleteMultipartUpload"
    }
  }
}
```

`demo-bucket` in the resource is the ID of the bucket used for Terraform. If we use differemt buckets, it should be unique, so we can perform operations referring to it with `google_storage_bucket.demo-bucket`.

**name** of the bucket should be unique globally in the entire Google Cloud Storage: `"course-data-engineering-demo-bucket"`

**force_destroy = true** means that the bucket will be destroyed in **age = 3** days.

Now let's create our Terraform plan:

```bash
terraform plan
```

It will show which actions Terraform will perform with which parameters when we are ready do deploy.

If everything looks good, let's do ahead and run

```bash
terraform apply
```

It will show a list of planned changes ans ask if we want to proceed.

After enetering "yes" it will perform all the actions and create a `terraform.tfstate` file.
It contains the current state of the infrastructure.

Now we want to remove this bucket.

Run `terraform destroy`. It will go though `terraform.tfstate` and check what action it should perfrom to delete resources.

Type "yes" to confirm.

Result:

```bash
# google_storage_bucket.demo-bucket: Destroying... [id=course-data-engineering-demo-bucket]
# google_storage_bucket.demo-bucket: Destruction complete after 2s

# Destroy complete! Resources: 1 destroyed.
```

## Terraform variables

Let's create a BigQuery dataset: https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/bigquery_dataset

Paste into main.tf

```terraform
resource "google_bigquery_dataset" "demo_dataset" {
  dataset_id = "demo_dataset"
  location   = "europe-west2"
}
```

And run `terraform apply`.

Output:

```bash
# google_bigquery_dataset.demo_dataset: Creating...
# google_storage_bucket.demo-bucket: Creating...
# google_bigquery_dataset.demo_dataset: Creation complete after 2s [id=projects/course-data-engineering/datasets/demo_dataset]
# google_storage_bucket.demo-bucket: Creation complete after 4s [id=course-data-engineering-demo-bucket]

# Apply complete! Resources: 2 added, 0 changed, 0 destroyed.
```

Ok, it works, now let's destroy the resources.

```bash
terraform destroy
```

Create a file named `variables.tf`.

Here we can define variables like this:

```
variable "bq_dataset_name" {
    description = "My BigQuery Dataset Name"
    default     = "demo_dataset"
}
```

We can reference variables in the `.tf` files like this:

```
name = var.gcs_bucket_name
```

Change string with variables where needed in `main.tf` and run `terraform apply`.

Output:

```bash
# google_bigquery_dataset.demo_dataset: Creating...
# google_storage_bucket.demo-bucket: Creating...
# google_bigquery_dataset.demo_dataset: Creation complete after 2s [id=projects/course-data-engineering/datasets/demo_dataset]
# google_storage_bucket.demo-bucket: Creation complete after 5s [id=course-data-engineering-demo-bucket]

# Apply complete! Resources: 2 added, 0 changed, 0 destroyed.
```

Run `terraform destroy`.

### Credentials in variables

We can specify credentials variable in the variables.tf and paste a path to our .json file.

Terraform has a built-in file() function, which reads the contents of a file at a given path and returns them as a string:

```
variable "credentials" {
    description = "My service account key"
    default = "secrets/terraform-sa-course-data-engineering-2e97d246cf4a.json"
}
```

# Setting up the Environment on Google Cloud

First we need to generate SSH keys.\
Instruction: https://cloud.google.com/compute/docs/connect/create-ssh-keys

```bash
ssh-keygen -t rsa -f ~/.ssh/<KEY_FILENAME> -C <USERNAME>
```

Replace the following:

- `KEY_FILENAME`: the name for your SSH key file.

  For example, a filename of `my-ssh-key` generates a private key file named `my-ssh-key` and a public key file named `my-ssh-key.pub`.
  
- `USERNAME`: your username on the VM. For example `cloudysanfrancisco`, or `cloudysanfrancisco_gmail_com`.

  For Linux VMs, the `USERNAME` can't be `root`, unless you configure your VM to allow root login.

```bash
ssh-keygen -t rsa -f ~/.ssh/de-course -C m
```

It generates two keys:
- `de-course` (private)
- `de-course` (public)

Now navigate to **Compute Engine** -> **Metadata** in GCP.

Enable Compute Engine API if asked.

Click **Add SSH Key** and copy output from: 

```bash
cat de-course.pub
```

All VMs in this project are now have access to this SSH key.

Navigate to **VM instances** -> **Create instance**.

Config:
- Region: europe-west2 (London)
- Series: E2
- Machine type: e2-standard-4 (4 vCPU, 2 core, 16 GB memory)
- Operating system: Ubuntu 24.04 LTS (x86/64, amd64)
- Disk: 30 GB

> **Monthly estimate: $129.65\
That's about $0.18 hourly**

Click **Create**.

Once it is created copy **External IP**.

Then navigate to Terminal and connect to the VM:

```bash
ssh -i <PRIVATE SSH KEY PATH> <USERNAME FROM SSH KEY>@<VM IP ADDRESS>
```

```bash
ssh -i ~/.ssh/de-course m@35.189.77.12
```

We already have `gcloud` SDK installed on this VM, check it:

```bash
gcloud --version
```

``` bash
# Google Cloud SDK 508.0.0
# alpha 2025.01.24
# beta 2025.01.24
# bq 2.1.12
# bundled-python3-unix 3.11.9
# core 2025.01.24
# gcloud-crc32c 1.0.0
# gsutil 5.33
# minikube 1.34.0
# skaffold 2.13.1
```

## Configure VM instance

Create a file named `config` in the `.ssh` folder on a local machine. We will use it for configuring SSH access to the VM.

Specify the following parameters:

```bash
Host test-de-course-instance  # just an alias
  HostName 35.189.77.12  # External IP
  User m  # username from SSH key
  IdentityFile ~/.ssh/de-course  # path to the private key
```

So now we can ssh into our VM using just an alias from config:

```bash
ssh test-de-course-instance
```

## Configure VS Code to work with remote VM

We can use visual code editor for work on remote VM.

Go to Extensions and install **Remote SSH**.

After it's installed in the bottom left corner click the arrows icon ("Open a remote window") and select **Connect to host**.\ Because we added our VM to the configuration file previously (`"test-de-course-instance"`), it will be available in the list.

Select it and a new VS Code window will open and connect to our VM via SSH.

Now let's clone the course repo:

```bash
https://github.com/DataTalksClub/data-engineering-zoomcamp.git
```

Cool, now we have access to the project's folder in VS code. 

## Configure uv

In the video Alexey uses Anaconda for managing Python in the VM, I'll be using [uv](https://github.com/astral-sh/uv).

Install uv:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Then, to add `$HOME/.local/bin` to the PATH, either restart shell or run:

```bash
source $HOME/.local/bin/env
```

Add uv and uvx autocompletion for bash:

```bash
echo 'eval "$(uv generate-shell-completion bash)"' >> ~/.bashrc
echo 'eval "$(uvx --generate-shell-completion bash)"' >> ~/.bashrc
```

## Docker installation

### Install Docker Engine

Set up Docker's apt repository:

```bash
# Add Docker's official GPG key:
sudo apt-get update
sudo apt-get install ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

# Add the repository to Apt sources:
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "${UBUNTU_CODENAME:-$VERSION_CODENAME}") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update
```

And install Docker Engine:

```bash
sudo apt update
sudo apt install docker.io
```

On Ubuntu regular users are not allowed to run docker commands without root.

To fix this, follow the instructions described here: https://docs.docker.com/engine/install/linux-postinstall/.

TL;DR:

```bash
sudo groupadd docker
sudo usermod -aG docker $USER
```

Logout + login and then try to `docker container run hello-world`.

```bash
# Hello from Docker!
# This message shows that your installation appears to be working correctly.
```

👍

### Install Docker Compose

It is better to install docker compose as a plugin, because it uses `docker compose` syntax instead of` docker-compose`: https://docs.docker.com/compose/install/linux/.

Make sure that [Docker's apt repository is installed](https://docs.docker.com/engine/install/ubuntu/#install-using-the-repository).

Then:

```bash
sudo apt-get update
sudo apt-get install docker-compose-plugin
```


## Install pgcli

```bash
uv add psycopg-binary
uv add pgcli
```

Try to connect:

```bash
pgcli -h localhost -p 5432 -u root -d ny_taxi
```

👍

## Port forwarding

We can forward ports of Postgres DB running in Docker on the VM to access it from our local machine.

Open Ports tab in VS code (near Terminal) and click Forward a Port.\
Enter `5432` into a Port field. Forwarded address will be set to `localhost:5432`.

Now we can access Postgres database from our local machine using `pgcli`:

```bash
pgcli -h localhost -p 5432 -u root -d ny_taxi
```

Do the same for port 8080 to get access to the pgAdmin UI.

Go to http://localhost:8080/

👍


## Upload data to the database

Let's ingest data to the DB using `upload_data.ipynb`.

Add all dependencies with `uv`:

```bash
uv add ipykernel pandas sqlalchemy psycopg2-binary
```

Download csv to the project directory:

```bash
wget https://github.com/DataTalksClub/nyc-tlc-data/releases/download/yellow/yellow_tripdata_2021-01.csv.gz
```

And run `upload_data.ipynb` notebook.

Data will be ingested into the `yellow_taxi_data` table.

## Install Terraform

Install via `apt`:

```bash
wget -O - https://apt.releases.hashicorp.com/gpg | sudo gpg --dearmor -o /usr/share/keyrings/hashicorp-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/hashicorp.list
sudo apt update && sudo apt install terraform
```

`terraform --version` output:

```bash
# Terraform v1.10.5
# on linux_amd64
```

To run terraform commands, we need to copy our service account json to the VM.

We'll use `sftp` for that.

On a local machine, navigate to the `secrets` folder where our service account json is stored.

Connect to our VM via `sftp`:

```bash
sftp test-de-course-instance
```

```bash
mkdir secrets
cd secrets
put terraform-sa-course-data-engineering-2e97d246cf4a.json
```

## Authenticate to Google Cloud using gcloud

Set the `GOOGLE_APPLICATION_CREDENTIALS` enviromment variable in the VM:

```bash
export GOOGLE_APPLICATION_CREDENTIALS=/home/m/code/secrets/terraform-sa-course-data-engineering-2e97d246cf4a.json
```

Check it with

```bash
echo $GOOGLE_APPLICATION_CREDENTIALS
```

Now we should authenticate to Google Cloud:

```bash
gcloud auth activate-service-account --key-file $GOOGLE_APPLICATION_CREDENTIALS
```

Output:

```bash
# Activated service account credentials for: [terraform-sa@course-data-engineering.iam.gserviceaccount.com]
```

👍

## Run Terraform

```bash
terraform init
terraform validate
terraform plan
terraform apply
terraform destroy
```

## Stop VM

From CLI:

```bash
sudo shutdown now
```

Or from GCP console.

(stopping a VM will take some time.)

❗️ After stopping and starting a VM again, a new external IP may be assigned to it.
In this case we need to connect to a new IP, and edit our `.ssh/config` file.

If we stop VM, we won't be charged for running instance, but still be charged for storage, because after starting a VM again our filesystem is preserved.

❗️ After stopping a VM all Docker containers will also be stopped.

After starting a VM containers are still will be available, just start them with docker compose:

```bash
docker compose start
```
