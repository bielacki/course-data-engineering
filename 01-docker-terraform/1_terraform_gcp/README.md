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

