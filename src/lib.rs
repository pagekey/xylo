pub mod cli;

use std::fs;
use std::path::Path;


pub fn new_project(name: &String) {
    println!("New project!: {}",name);
    fs::create_dir(name);
}


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
}
