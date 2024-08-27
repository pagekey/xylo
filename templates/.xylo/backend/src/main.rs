use warp::Filter;


#[tokio::main]
async fn main() {
    println!("Starting backend.");
    let cors = warp::cors()
        .allow_any_origin();

    let hello = warp::path::end()
        .map(|| warp::reply::html("hello world"))
        .with(cors);

    // Start the warp server
    warp::serve(hello)
        .run(([127, 0, 0, 1], 5000))
        .await;
}
