use core::arch;
use log::info;
use minijinja;
use serde_json;
use std::fs;

fn register_drra_library() {
    // Get the VESYLA_SUITE_PATH_COMPONENTS environment variable
    let vesyla_suite_path_components = std::env::var("VESYLA_SUITE_PATH_COMPONENTS")
        .expect("VESYLA_SUITE_PATH_COMPONENTS environment variable is not set");
    // Execute sst-register command
    let output = std::process::Command::new("sst-register")
        .arg("drra")
        .arg(format!("drra_LIBDIR={}", vesyla_suite_path_components))
        .output()
        .expect("Failed to execute sst-register command");

    if !output.status.success() {
        panic!("sst-register command failed: {:?}", output);
    }
}

fn gen_sst_config(arch_file: &String, output_dir: &String) {
    let output_dir = std::path::Path::new(output_dir);
    if !output_dir.exists() {
        fs::create_dir_all(output_dir).expect("Failed to create output directory");
    }

    let json_str = std::fs::read_to_string(arch_file).expect("Failed to read file");
    let arch: serde_json::Value = serde_json::from_str(&json_str).expect("Failed to parse json");

    // Apply the template
    let template = include_str!("../sst/sst_sim_template.py.j2");
    let mut context = minijinja::Environment::new();
    context.add_template("sst_sim_template", template).unwrap();
    let result = context
        .get_template("sst_sim_template")
        .unwrap()
        .render(&arch);
    let output = result.expect("Failed to render template");

    // Write the output to a file
    let output_file = output_dir.join("sst_sim_conf.py");
    fs::write(&output_file, output).expect("Failed to write output file");

    info!(
        "Generated SST configuration file: {:?}",
        output_file.to_str().unwrap()
    );
}

pub fn generate(arch_file: &String, output_dir: &String) {
    register_drra_library();
    gen_sst_config(arch_file, output_dir);
}
