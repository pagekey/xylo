pub mod cli;

use std::fs;
use std::path::Path;
use std::process::Command;


pub fn new_project(name: &String) {
    println!("New project!: {}",name);
    fs::create_dir(name);
}

fn command_successful(command: &str) -> bool {
    let mut parts_iter = command.split_whitespace();
    let command_name: &str = parts_iter.next().expect("Failed to parse command.");
    let args: Vec<&str> = parts_iter.collect();
    let result = Command::new(command_name)
        .args(args)
        .output();
    match result {
        Ok(output) => output.status.success(),
        Err(error) => false
    }
}
// fn requirements_installed() -> bool {
//     let output = Command::new("npx")
//         .arg("--version")
//         .output()
//         .expect("Failed to execute command");
//     output.status.success()
// }


#[cfg(test)]
mod tests {
    use super::*;
    use std::env;
    use tempdir::TempDir;

    #[test]
    fn test_new_project_creates_dir_with_file() {
        let name = "xyloproject";

        let original_dir = env::current_dir().expect("Failed to get current directory.");
        let temp_dir = TempDir::new(name).expect("Failed to create temporary directory.");
        let dir_path = temp_dir.path();
        env::set_current_dir(&dir_path).expect("Failed to change directory.");
        
        new_project(&name.to_string());

        let file_path = format!("{}", name);
        assert!(Path::new(&file_path).exists());

        env::set_current_dir(&original_dir).expect("Failed to change directory back.");
        temp_dir.close().expect("Failed to delete temporary directory.");
    }

    #[test]
    fn test_command_successful_returns_true_for_successful_command() {
        assert_eq!(command_successful("echo hi"), true);
    }
    #[test]
    fn test_command_successful_returns_false_for_failed_command() {
        assert_eq!(command_successful("false"), false);
    }
    #[test]
    fn test_command_successful_returns_false_for_command_not_found() {
        assert_eq!(command_successful("this-is-not-a-valid-command someargs"), false);
    }
}
