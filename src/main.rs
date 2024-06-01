extern crate pagekey_xylo as xylo;

use xylo::cli::{Cli, ProjectHandler, DefaultProjectHandler};
use structopt::StructOpt;


fn main() {
    let args = Cli::from_args();
    let handler = DefaultProjectHandler;
    handler.handle(&args);
}
