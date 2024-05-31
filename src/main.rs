use structopt::StructOpt;

mod cli;
use cli::{Cli, ProjectHandler, DefaultProjectHandler};


fn main() {
    let args = Cli::from_args();
    let handler = DefaultProjectHandler;
    handler.handle(&args);
}
