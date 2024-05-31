pub mod cli;
pub mod system_caller;

use std::fs;
use std::path::Path;
use system_caller::SystemCaller;


pub fn new_project(name: &String) {
    println!("New project!: {}",name);
    fs::create_dir(name).expect("Failed to create folder.");
    fs::create_dir(Path::new(name).join("frontend")).expect("Failed to create folder.");
    fs::create_dir(Path::new(name).join("backend")).expect("Failed to create folder.");
}

fn requirements_installed(system_caller: &mut dyn SystemCaller) -> bool {
    system_caller.command_successful("npx --version")
}


#[cfg(test)]
mod tests {
    use super::*;
    use std::env;
    use tempdir::TempDir;

    #[test]
    fn test_new_project_creates_dir_with_file() {
        // TODO this is more of an integration test - move to tests/ folder
        let name = "xyloproject";

        let original_dir = env::current_dir().expect("Failed to get current directory.");
        let temp_dir = TempDir::new(name).expect("Failed to create temporary directory.");
        let dir_path = temp_dir.path();
        env::set_current_dir(&dir_path).expect("Failed to change directory.");
        
        new_project(&name.to_string());

        let file_path = format!("{}", name);
        assert!(Path::new(&file_path).exists());
        assert!(Path::new(&file_path).join("frontend").exists());
        assert!(Path::new(&file_path).join("backend").exists());

        env::set_current_dir(&original_dir).expect("Failed to change directory back.");
        temp_dir.close().expect("Failed to delete temporary directory.");
    }
}
