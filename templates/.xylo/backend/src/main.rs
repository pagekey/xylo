use std::thread;
use std::time::Duration;
use warp::Filter;


#[tokio::main]
async fn main() {
    println!("Starting backend.");
    let hello = warp::path::end()
        .map(|| warp::reply::html("hello world"));

    // Start the warp server
    warp::serve(hello)
        .run(([127, 0, 0, 1], 5000))
        .await;
}
