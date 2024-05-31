use structopt::StructOpt;
use crate::new_project;

#[derive(StructOpt, Debug, PartialEq)]
#[structopt(name="xylo", about="Self-hosted app creation kit")]
pub enum Cli {
    New {
        project_name: String,
    }
}

pub trait ProjectHandler {
    fn handle(&self, cli: &Cli);
    fn handle_new(&self, project_name: &String);
}
pub struct DefaultProjectHandler;
impl ProjectHandler for DefaultProjectHandler {
    fn handle(&self, cli: &Cli) {
        match cli {
            Cli::New { project_name } => self.handle_new(project_name)
        }
    }
    fn handle_new(&self, project_name: &String) {
        new_project(project_name);
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
}
