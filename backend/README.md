# Python Virtual Environment Setup Guide

## Prerequisites

-   Python installed on your system
-   pip (Python package installer)

## Steps to Create and Initialize a Virtual Environment

1. Open terminal/command prompt in your project directory

2. Create a virtual environment:

    ```python
    python -m venv .venv
    ```

3. Activate the virtual environment:

    **Windows:**

    ```cmd
    .venv\Scripts\activate
    ```

    **Unix/MacOS:**

    ```bash
    source venv/bin/activate
    ```

4. Verify activation:

    - Your prompt should change to show `(venv)`
    - Run `which python` (Unix/MacOS) or `where python` (Windows) to confirm using venv Python

5. Install packages:

    ```python
    pip install -r requirements.txt  # if you have requirements file
    # or install packages individually
    pip install package_name
    ```

6. To deactivate when done:
    ```bash
    deactivate
    ```

steps to create and initilize a python venv
