pub mod cli;
pub mod system_caller;

use std::env;
use std::fs;
use std::io::Write;
use std::path::Path;
use std::process::{Child, Command};
use rust_embed::RustEmbed;
use walkdir::WalkDir;

use std::sync::atomic::{AtomicBool, Ordering};
use std::sync::Arc;
use std::time::Duration;
use std::thread;

#[derive(RustEmbed)]
#[folder="templates/"]
struct Asset;


fn copy_template_files() {
    // Copy files from template
    for file in Asset::iter() {
        let file_in = Asset::get(file.as_ref()).unwrap();
        let file_out_path = Path::new(if file.as_ref() == ".ignore" { ".gitignore" } else { file.as_ref() });
        if let Some(dir) = file_out_path.parent() {
            fs::create_dir_all(dir).unwrap();
        }
        
        if !Path::new(file_out_path).exists() {
            let mut file_out = fs::File::create(file_out_path).expect("Failed to create file.");
            let content = file_in.data.as_ref();
            file_out.write_all(content).expect("Failed to write template content to file.");
        }
    }
}

pub fn run_new(name: &String) {
    println!("New project!: {}",name);
    // Generate directories and empty files
    fs::create_dir(name).expect("Failed to create folder.");
    fs::File::create(Path::new(name).join("xylo.yaml")).expect("Failed to create xylo.yaml.");
    // cd into frontend and generate next project
    let original_dir = env::current_dir().expect("Could not get current directory.");
    env::set_current_dir(Path::new(name)).expect("Could not change current directory.");

    copy_template_files();
    // Restore original directory
    env::set_current_dir(original_dir).expect("Could not change current directory.");
}

pub fn run_dev() {
    if Path::new("xylo.yaml").exists() {
        copy_template_files();
        let original_dir = env::current_dir().expect("Could not get current directory.");

        // Copy all files for frontend/backend into the .xylo dir
        for entry in WalkDir::new("backend").into_iter().filter_map(Result::ok) {
            if entry.file_type().is_file() {
                if let Some(dir) = entry.path().parent() {
                    let target_dir = Path::new(".xylo").join(dir);
                    fs::create_dir_all(target_dir).unwrap();
                }
                let target_path = Path::new(".xylo").join(entry.path());
                fs::copy(entry.path(), target_path).expect("Failed to copy file.");
            }
        }
        for entry in WalkDir::new("frontend").into_iter().filter_map(Result::ok) {
            if entry.file_type().is_file() {
                if let Some(dir) = entry.path().parent() {
                    let target_dir = Path::new(".xylo").join(dir);
                    fs::create_dir_all(target_dir).unwrap();
                }
                let target_path = Path::new(".xylo").join(entry.path());
                println!("Copying {}", target_path.display());
                fs::copy(entry.path(), target_path).expect("Failed to copy file.");
            }
        }
        // Watch for changes and copy files when change detected.
        // TODO implement

        println!("Installing dependencies...");
        Command::new("npm")
            .args(vec!["install"])
            .current_dir(original_dir.join(".xylo").join("frontend"))
            .output()
            .expect("Failed to install deps.");

        // Set up CTRL-C handler
        let running = Arc::new(AtomicBool::new(true)); // for frontend thread
        let r = running.clone(); // for ctrl-c handler
        let r2 = running.clone(); // for backend thread

        ctrlc::set_handler(move || {
            println!("CTRL-C pressed");

            r.store(false, Ordering::SeqCst);
        }).expect("Error setting CTRL-C handler.");

        println!("Frontend listening on http://localhost:3000");
        
        let frontend_handle = thread::spawn(move || {
            let mut child: Option<Child> = None;
            while running.load(Ordering::SeqCst) {
                if child.is_none() {
                    let original_dir = env::current_dir().expect("Could not get current directory.");
                    child = Some(Command::new("npm")
                        .args(vec!["run","dev"])
                        .current_dir(original_dir.join(".xylo").join("frontend"))
                        .spawn()
                        .expect("Failed to start frontend dev server."));
                }

                if let Some(ref mut c) = child {
                    match c.try_wait() {
                        Ok(Some(status)) => {
                            println!("Frontend exited with status: {}", status);
                            break;
                        }
                        Ok(None) => {
                            // Still running
                        }
                        Err(e) => {
                            println!("Error checking command status: {}", e);
                            break;
                        }
                    }
                }

                thread::sleep(Duration::from_millis(100));
            }
            if let Some(mut c) = child {
                c.kill().expect("Failed to kill frontend.");
                println!("Frontend killed.")
            }
        });
        let backend_handle = thread::spawn(move || {
            let mut child: Option<Child> = None;
            while r2.load(Ordering::SeqCst) {
                if child.is_none() {
                    let original_dir = env::current_dir().expect("Could not get current directory.");
                    child = Some(Command::new("cargo")
                        .args(vec!["run"])
                        .current_dir(original_dir.join(".xylo").join("backend"))
                        .spawn()
                        .expect("Failed to start backend server."));
                }

                if let Some(ref mut c) = child {
                    match c.try_wait() {
                        Ok(Some(status)) => {
                            println!("Backend exited with status: {}", status);
                            break;
                        }
                        Ok(None) => {
                            // Still running
                        }
                        Err(e) => {
                            println!("Error checking command status: {}", e);
                            break;
                        }
                    }
                }

                thread::sleep(Duration::from_millis(100));
            }
            if let Some(mut c) = child {
                c.kill().expect("Failed to kill backend.");
                println!("Backend killed.")
            }
        });

        frontend_handle.join().unwrap();
        backend_handle.join().unwrap();
        println!("Done.");
    } else {
        eprintln!("xylo.yaml not found - you are not in a xylo project. Generate one with `xylo new`.");
    }
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
        assert!(Path::new(&file_path).join(".xylo").join("frontend").join("package.json").exists());
        assert!(Path::new(&file_path).join("backend").exists());
        assert!(Path::new(&file_path).join("xylo.yaml").exists());

        env::set_current_dir(&original_dir).expect("Failed to change directory back.");
        temp_dir.close().expect("Failed to delete temporary directory.");
    }
}
