pub mod cli;
pub mod system_caller;

use std::env;
use std::fs;
use std::io::Write;
use std::path::Path;
use std::process::Command;
use system_caller::{ProductionSystemCaller, SystemCaller};
use rust_embed::RustEmbed;

#[derive(RustEmbed)]
#[folder="templates/"]
struct Asset;


pub fn run_new(name: &String) {
    println!("New project!: {}",name);
    // Generate directories and empty files
    fs::create_dir(name).expect("Failed to create folder.");
    fs::create_dir(Path::new(name).join("frontend")).expect("Failed to create folder.");
    fs::create_dir(Path::new(name).join("backend")).expect("Failed to create folder.");
    fs::File::create(Path::new(name).join("xylo.yaml")).expect("Failed to create xylo.yaml.");
    // cd into frontend and generate next project
    let original_dir = env::current_dir().expect("Could not get current directory.");
    env::set_current_dir(Path::new(name).join("frontend")).expect("Could not change current directory.");
    let npx_args = format!("npx create-next-app@13 {} --typescript --eslint --tailwind --src-dir --no-app --import-alias @/*", name);
    Command::new("npx").args(npx_args.as_str().split_whitespace()).output().expect("Failed to create next project.");
    // Move everything in the generated folder up one level
    let entries = fs::read_dir(Path::new(name)).expect("Failed to read directory.");
    for entry in entries {
        let entry = entry.expect("Failed to list file.");
        fs::rename(entry.path(), entry.file_name()).expect("Failed to rename file.");
    }
    // Remove the nested (now empty) frontend dir
    fs::remove_dir(Path::new(name)).expect("Failed to remove nested directory.");
    // Install mantine
    let npm_args = "i --save-dev postcss postcss-preset-mantine postcss-simple-vars";
    Command::new("npm").args(npm_args.split_whitespace()).output().expect("Failed to install dev deps for mantine.");
    let npm_args = "i --save @mantine/core @mantine/hooks";
    Command::new("npm").args(npm_args.split_whitespace()).output().expect("Failed to install deps for mantine.");

    // Try outputting a template file
    if let Some(file) = Asset::get("index.html") {
        let content = file.data.as_ref();
        let path = Path::new("index.html");
        let mut file = fs::File::create(path).expect("Failed to create file.");
        file.write_all(content).expect("Failed to write template content to file.");
        println!("Copied template.");
    } else {
        eprintln!("Failed to render template.");
    }

    // Restore original directory
    env::set_current_dir(original_dir).expect("Could not change current directory.");
}

pub fn run_dev() {
    println!("Frontend listening on http://localhost:3000");
    // TODO check if xylo.yaml is in the current dir
    let original_dir = env::current_dir().expect("Could not get current directory.");
    env::set_current_dir(Path::new("frontend")).expect("Could not change current directory.");
    // TODO run command in background
    Command::new("npm").args(vec!["run","dev"]).output().expect("Failed to start frontend dev server.");
    env::set_current_dir(original_dir).expect("Could not change current directory.");
}

fn requirements_installed(system_caller: &mut dyn SystemCaller) -> bool {
    system_caller.command_successful("npx --version")
}


#[cfg(test)]
mod tests {
    use super::*;
    use tempdir::TempDir;

    #[test]
    fn test_new_project_creates_dir_with_file() {
        // TODO this is more of an integration test - move to tests/ folder
        let name = "xyloproject";

        let original_dir = env::current_dir().expect("Failed to get current directory.");
        let temp_dir = TempDir::new(name).expect("Failed to create temporary directory.");
        let dir_path = temp_dir.path();
        env::set_current_dir(&dir_path).expect("Failed to change directory.");
        
        run_new(&name.to_string());

        let file_path = format!("{}", name);
        assert!(Path::new(&file_path).exists());
        assert!(Path::new(&file_path).join("frontend").exists());
        assert!(Path::new(&file_path).join("frontend").join("package.json").exists());
        assert!(Path::new(&file_path).join("backend").exists());
        assert!(Path::new(&file_path).join("xylo.yaml").exists());

        env::set_current_dir(&original_dir).expect("Failed to change directory back.");
        temp_dir.close().expect("Failed to delete temporary directory.");
    }
}
