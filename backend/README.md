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

## Steps to Run This Project

1. **Install Packages**:

    - Navigate to the [backend](http://_vscodecontentref_/0) folder.
    - Install the required packages from the `requirements.txt` file:

    ```bash
    pip install -r requirements.txt
    ```

2. **Delete Database Tables**:

    - Run `api_test.py` from the `src` folder to delete the database tables:

    ```bash
    python src/api_test.py
    ```

3. **Start the Application**:

    - Run `main.py` using `uvicorn` from the `src` folder:

    ```bash
    uvicorn src.main:app --reload
    ```

4. **Re-create Tables**:
    - If `api_test.py` is executed, you will need to re-run `main.py` to re-create the tables.
