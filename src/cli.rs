use structopt::StructOpt;
use crate::{run_new, run_dev};

#[derive(StructOpt, Debug, PartialEq)]
#[structopt(name="xylo", about="Self-hosted app creation kit")]
pub enum Cli {
    New {
        project_name: String,
    },
    Dev,
}

pub trait ProjectHandler {
    fn handle(&self, cli: &Cli);
    fn handle_new(&self, project_name: &String);
    fn handle_dev(&self);
}
pub struct DefaultProjectHandler;
impl ProjectHandler for DefaultProjectHandler {
    fn handle(&self, cli: &Cli) {
        match cli {
            Cli::New { project_name } => self.handle_new(project_name),
            Cli::Dev => self.handle_dev(),
        }
    }
    fn handle_new(&self, project_name: &String) {
        run_new(project_name);
    }
    fn handle_dev(&self) {
        run_dev();
    }
}


#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_parse_new() {
        let cli = Cli::from_iter(&["xylo", "new", "myproject"]);
        assert_eq!(cli, Cli::New { project_name: "myproject".into() });
    }

    #[test]
    fn test_parse_dev() {
        let cli = Cli::from_iter(&["xylo", "dev"]);
        assert_eq!(cli, Cli::Dev);
    }
}
