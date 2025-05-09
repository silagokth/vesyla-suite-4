# vesyla

Tool suite for DRRA-2 hardware accelerator platform.

## Projects

- vs-manas: Low level assembler for DRRA-2 ISA
- vs-testcase: Test case infrastructure and build-in test cases for DRRA-2
- vs-entry: Entry point for vesyla
- vs-schedule: Scheduler for DRRA-2 instruction. It will be integrated into the future compiler
- vs-component: Assemble the components of vesyla, it requires you to specify the location of DRRA libary as enviroment variable `VESYLA_SUITE_PATH_COMPONENTS`. Check the repo [drra-components](https://github.com/silagokth/drra-components).

## Compile and Install

1. Install dependencies:

    ```bash
    sh ./scripts/install_dependencies.sh
    ```

2. Generate the Vesyla appimage:

    ```bash
    sh ./scripts/make_appimage.sh
    ```

3. Copy the appimage (`./vesyla`) to your `PATH`, for example:

    ```bash
    chmod +x ./vesyla
    sudo mv ./vesyla /usr/local/bin/vesyla
    ```
