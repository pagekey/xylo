use std::thread;
use std::time::Duration;


fn main() {
    println!("Starting backend.");
    loop {
        println!("Sleeping backend.");
        thread::sleep(Duration::from_secs(10));
    }
}
