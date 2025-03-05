# Installing Apache Spark in virtual environment on macOS using Homebrew

## 0. Install Homebrew

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

## 1. Install uv

```bash
brew unstall uv
```

## 2. Install Java

JDK - Java Development Kit.

Install `openjdk@17` globally with brew:

```bash
brew install openjdk@17
```

For the system Java wrappers to find this JDK, symlink it:

- for Apple Silicon chips:

    ```
    sudo ln -sfn /opt/homebrew/opt/openjdk@17/libexec/openjdk.jdk /Library/Java/JavaVirtualMachines/openjdk-17.jdk
    ```

- for Intel chips:

    ```
    sudo ln -sfn /usr/local/opt/openjdk@17/libexec/openjdk.jdk /Library/Java/JavaVirtualMachines/openjdk-17.jdk
    ```

Then run:

```
java -version
```

If output is like the following, then everything is ok:

```
openjdk version "17.0.14" 2025-01-21
OpenJDK Runtime Environment Homebrew (build 17.0.14+0)
OpenJDK 64-Bit Server VM Homebrew (build 17.0.14+0, mixed mode, sharing)
```

## 3. Create a virtual environment with uv

cd to a project's folder.

Then specify Python version, and initialize uv. This will also create a virtual environment and add a .venv directory.

```bash
uv python pin 3.10\
uv venv\
uv init --bare
```

## 4. Install pyspark

```bash
uv add pyspark
```

## 5. Verufy installation

Activate virtual environment:

```
source .venv/bin/activate
```

and run 

```
pyspark
```

If output is like the following, then everything is ok:

```
Python 3.10.15 (main, Oct 16 2024, 08:33:15) [Clang 18.1.8 ] on darwin
Type "help", "copyright", "credits" or "license" for more information.
Setting default log level to "WARN".
To adjust logging level use sc.setLogLevel(newLevel). For SparkR, use setLogLevel(newLevel).
25/03/04 21:26:11 WARN NativeCodeLoader: Unable to load native-hadoop library for your platform... using builtin-java classes where applicable
Welcome to
      ____              __
     / __/__  ___ _____/ /__
    _\ \/ _ \/ _ `/ __/  '_/
   /__ / .__/\_,_/_/ /_/\_\   version 3.5.3
      /_/

Using Python version 3.10.15 (main, Oct 16 2024 08:33:15)
Spark context Web UI available at http://192.168.0.45:4040
Spark context available as 'sc' (master = local[*], app id = local-1741119971399).
SparkSession available as 'spark'.
>>>
```


Ctrl + Z to exit spark session.
