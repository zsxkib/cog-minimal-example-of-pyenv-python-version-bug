# Cog `.python-version` vs `cog.yaml` conflict: Minimal reproducible example

This repository shows a bug in [Cog](https://github.com/replicate/cog) where `cog predict` can fail when starting its container. This happens if you have a `.python-version` file in your project that asks for a different Python version than your `cog.yaml` file does.

*(This was observed with Cog version `0.14.4`)*

**GitHub Issue:** [replicate/cog#2275](https://github.com/replicate/cog/issues/2275)

## What's happening?

Cog uses a tool called `pyenv` inside its build containers to handle Python versions. Your `cog.yaml` file tells Cog which Python version to install when it builds the container image (for example, `python_version: "3.11"`).

But, if you also have a file named `.python-version` in your project's main directory, Cog copies that file into the container image too. When the container starts up, `pyenv` sees the `.python-version` file and tries to use the Python version specified *in that file* (say, `3.10`).

If the version in your `.python-version` file (like `3.10`) doesn't match the version Cog actually installed based on `cog.yaml` (like `3.11`), `pyenv` gives up and causes `cog predict` to stop with an error like this:

```
pyenv: version `<version from .python-version>` is not installed (set by /src/.python-version)
ⅹ Failed to get container status: exit status 1
```

This error happens during the container's startup, even if the Docker image itself built just fine.

**Good to know:** Running `cog init` doesn't create a `.python-version` file for you. You might have one if you cloned a project from somewhere else or if another tool created it.

## How this repository shows the bug

We've set up this repository so you can see the bug in action:

1.  **Working setup (this is how the repo starts):**
    *   The `.python-version` file asks for `3.10`.
    *   The `cog.yaml` file also asks for `python_version: "3.10"`.
    *   Because these match, `cog predict` works correctly.

2.  **Broken setup (after you change one file):**
    *   The `.python-version` file still asks for `3.10`.
    *   You change `cog.yaml` to ask for `python_version: "3.11"`.
    *   Now the versions don't match, and `cog predict` will fail with the `pyenv` error.

## Steps to reproduce the bug

1.  **Clone this repository:**
    ```bash
    git clone https://github.com/zsxkib/cog-minimal-example-of-pyenv-python-version-bug # Or your fork's URL
    cd cog-minimal-example-of-pyenv-python-version-bug
    ```
2.  **Run prediction (it should work):**
    Check that both `.python-version` and `cog.yaml` (look for `build.python_version`) specify `3.10`.
    ```bash
    sudo cog predict -i text="Works"
    ```
    *What you should see:* The prediction finishes, showing "hello world Works".

3.  **Create the version conflict:**
    Open `cog.yaml` in your editor and change `python_version` from `"3.10"` to `"3.11"`.
    ```yaml
    # cog.yaml
    build:
      # ...
      python_version: "3.11" # <-- Change this line
      # ...
    ```
4.  **Run prediction (it should fail):**
    Because you changed `cog.yaml`, Cog needs to rebuild the image.
    ```bash
    sudo cog predict -i text="Fails"
    ```
    *What you should see:* The Docker build might finish, but the prediction fails when the container tries to start, showing the `pyenv: version '3.10' is not installed...` error.

5.  **Fix the conflict:**
    Change `python_version` back to `"3.10"` in `cog.yaml`.

6.  **Run prediction (it should work again):**
    ```bash
    sudo cog predict -i text="Works Again"
    ```
    *What you should see:* The prediction finishes successfully.

## Ways to work around this

*   **Make the versions match:** The simplest fix is to make sure your `.python-version` file and the `python_version` in your `cog.yaml` ask for the exact same Python version.
*   **Remove `.python-version**:** If you don't need the `.python-version` file for other reasons (like local development outside of Cog), you can just delete it.
*   **Use `.dockerignore` (maybe):** Adding `.python-version` to your `.dockerignore` file *might* stop Cog from copying it into the container. However, when this bug was first found, this didn't seem to work reliably every time, so it might not be a perfect solution.

We hope this example helps figure out exactly why the `.python-version` file interferes with the Python environment Cog sets up based on `cog.yaml`.